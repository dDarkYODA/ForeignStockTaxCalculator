import os
import sys
import subprocess
import json
from github import Github
from openai import OpenAI

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout, result.returncode

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not all([github_token, repo_name, event_path]):
        print("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or GITHUB_EVENT_PATH.")
        sys.exit(1)

    if not openai_api_key:
        print("Warning: OPENAI_API_KEY is not set. AI Agent Loop cannot run.")
        print("Please configure OPENAI_API_KEY in your repository secrets to enable auto-fixes.")
        sys.exit(0)

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    client = OpenAI(api_key=openai_api_key)

    with open(event_path, 'r') as f:
        event_data = json.load(f)

    # Try different event structures for the PR number
    pr_number = None
    if "pull_request" in event_data:
        pr_number = event_data["pull_request"].get("number")
    elif "issue" in event_data:
        pr_number = event_data["issue"].get("number")

    if not pr_number:
        print(f"Could not find PR number in event: {event_data.keys()}")
        # Fallback for manual trigger or if the event structure is different
        pr_number = os.getenv("PR_NUMBER")

    if not pr_number:
        print("Could not find PR number. Exiting.")
        sys.exit(0)

    pr = repo.get_pull(int(pr_number))
    print(f"Processing PR #{pr_number}: {pr.title}")

    # 1. Fetch CodeRabbit comments
    comments = list(pr.get_review_comments())
    cr_comments = [c for c in comments if "coderabbit" in c.user.login.lower()]

    if not cr_comments:
        print("No CodeRabbit comments found.")

    # 2. Group by file
    files_to_fix = {}
    for comment in cr_comments:
        if comment.path not in files_to_fix:
            files_to_fix[comment.path] = []
        files_to_fix[comment.path].append(comment.body)

    if not files_to_fix:
        print("No unresolved CodeRabbit comments to process.")
    else:
        # 3. Load agent instructions
        with open(".ai/review-fix-agent.md", "r") as f:
            review_fix_instructions = f.read()
        with open(".ai/architecture-agent.md", "r") as f:
            arch_instructions = f.read()

        # 4. Apply fixes
        for path, comment_list in files_to_fix.items():
            if not os.path.exists(path):
                print(f"File {path} not found locally. Skipping.")
                continue

            with open(path, "r") as f:
                content = f.read()

            print(f"Fixing {path}...")

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

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )

            new_content = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting
            if new_content.startswith("```"):
                lines = new_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                new_content = "\n".join(lines)

            with open(path, "w") as f:
                f.write(new_content)

    # 5. Add tests
    print("Running test agent...")
    with open(".ai/test-agent.md", "r") as f:
        test_instructions = f.read()

    stdout, code = run_command("cd backend && pytest ../tests")
    if code != 0:
        print(f"Tests failed after fixes:\n{stdout}")

    # 6. Verify and commit
    run_command("git config user.name 'github-actions[bot]'")
    run_command("git config user.email 'github-actions[bot]@users.noreply.github.com'")
    run_command("git add .")

    # Check if there are changes to commit
    diff_check, _ = run_command("git diff --staged")
    if not diff_check.strip():
        print("No changes to commit.")
        return

    run_command("git commit -m 'AI: Auto-fix CodeRabbit comments and improve architecture'")
    run_command(f"git push origin HEAD:{pr.head.ref}")

    print("Fixes applied and pushed.")

if __name__ == "__main__":
    main()
