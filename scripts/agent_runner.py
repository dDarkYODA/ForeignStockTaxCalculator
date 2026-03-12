import os
import sys
import subprocess
import json
import time
import logging
from github import Github
from openai import OpenAI, APIError, RateLimitError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    logger.info(f"Running: {' '.join(cmd)}")
    try:
        # Use shell=False to avoid shell injection
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, shell=False)
        if result.returncode != 0:
            logger.error(f"Command failed with exit code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
        return result.stdout, result.returncode
    except Exception as e:
        logger.error(f"Exception running command {' '.join(cmd)}: {e}")
        return "", 1

def call_openai_with_retry(client, model, messages, max_retries=3):
    for i in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            if i < max_retries - 1:
                wait_time = (2 ** i) + 5
                logger.warning(f"Rate limit hit, retrying in {wait_time}s... ({e})")
                time.sleep(wait_time)
            else:
                logger.error("Rate limit hit, max retries reached.")
                raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {e}")
            raise

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not all([github_token, repo_name, event_path]):
        logger.error("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or GITHUB_EVENT_PATH.")
        sys.exit(1)

    if not openai_api_key:
        logger.warning("OPENAI_API_KEY is not set. AI Agent Loop cannot run.")
        logger.info("Please configure OPENAI_API_KEY in your repository secrets to enable auto-fixes.")
        sys.exit(0)

    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to read or parse event file at {event_path}: {e}")
        sys.exit(1)

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    client = OpenAI(api_key=openai_api_key)

    # Try different event structures for the PR number
    pr_number = None
    if "pull_request" in event_data:
        pr_number = event_data["pull_request"].get("number")
    elif "issue" in event_data:
        pr_number = event_data["issue"].get("number")

    if not pr_number:
        logger.info(f"Could not find PR number in event: {event_data.keys()}")
        pr_number = os.getenv("PR_NUMBER")

    if not pr_number:
        logger.info("Could not find PR number. Exiting.")
        sys.exit(0)

    pr = repo.get_pull(int(pr_number))
    logger.info(f"Processing PR #{pr_number}: {pr.title}")

    # 1. Fetch CodeRabbit comments
    comments = list(pr.get_review_comments())
    cr_comments = [c for c in comments if "coderabbit" in c.user.login.lower()]

    if not cr_comments:
        logger.info("No CodeRabbit comments found.")

    # 2. Group by file
    files_to_fix = {}
    for comment in cr_comments:
        if comment.path not in files_to_fix:
            files_to_fix[comment.path] = []
        files_to_fix[comment.path].append(comment.body)

    modified_files = []

    if not files_to_fix:
        logger.info("No unresolved CodeRabbit comments to process.")
    else:
        # 3. Load agent instructions
        try:
            with open(".ai/review-fix-agent.md", "r") as f:
                review_fix_instructions = f.read()
            with open(".ai/architecture-agent.md", "r") as f:
                arch_instructions = f.read()
        except FileNotFoundError as e:
            logger.error(f"Required agent instruction file not found: {e}")
            sys.exit(1)

        # 4. Apply fixes
        for path, comment_list in files_to_fix.items():
            full_path = os.path.join(os.getcwd(), path)
            if not os.path.exists(full_path):
                logger.warning(f"File {path} not found locally. Skipping.")
                continue

            with open(full_path, "r") as f:
                content = f.read()

            logger.info(f"Fixing {path}...")

            prompt = f"""
            Instructions: {review_fix_instructions}
            Architecture Context: {arch_instructions}

            File Path: {path}
            Current Content:
            ```
            {content}
            ```

            Comments to address:
            {chr(10).join(['- ' + c for c in comment_list])}

            Return ONLY the FULL updated file content. Do not include any other text, explanations or markdown wrappers.
            """

            try:
                new_content = call_openai_with_retry(client, "gpt-4o", [{"role": "user", "content": prompt}])

                # Clean up potential markdown formatting
                if new_content.startswith("```"):
                    lines = new_content.splitlines()
                    if lines and lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    new_content = "\n".join(lines)

                with open(full_path, "w") as f:
                    f.write(new_content)
                modified_files.append(path)
            except Exception as e:
                logger.error(f"Failed to fix {path}: {e}")

    # 5. Add tests / Verify
    logger.info("Running verification/tests...")
    # In a real implementation, we would use test_instructions to guide test generation/execution.
    # For now, we use them as a sanity check and ensure we fail the CI on test failure.
    try:
        with open(".ai/test-agent.md", "r") as f:
            test_instructions = f.read()
    except FileNotFoundError:
        logger.warning(".ai/test-agent.md not found.")

    # We use a custom command that handles the directory change safely
    # Note: PYTHONPATH is important here.
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    # Run tests from project root
    stdout, code = run_command(["python3", "-m", "pytest", "tests/"])
    if code != 0:
        logger.error(f"Tests failed after fixes. Halting.\n{stdout}")
        sys.exit(code)

    # 6. Verify and commit
    if not modified_files:
        logger.info("No changes to commit.")
        return

    run_command(["git", "config", "user.name", "github-actions[bot]"])
    run_command(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])

    # Explicitly add only the modified files to avoid staging unwanted artifacts
    for f in modified_files:
        run_command(["git", "add", f])

    # Check if there are changes to commit
    diff_check, _ = run_command(["git", "diff", "--staged"])
    if not diff_check.strip():
        logger.info("No changes in index after adding modified files.")
        return

    run_command(["git", "commit", "-m", "AI: Auto-fix CodeRabbit comments and improve architecture"])

    # Secure push using list args to avoid shell injection
    run_command(["git", "push", "origin", f"HEAD:{pr.head.ref}"])

    logger.info("Fixes applied and pushed successfully.")

if __name__ == "__main__":
    main()
