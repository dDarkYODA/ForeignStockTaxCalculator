import requests
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

def run_command(cmd, env=None, cwd=None):
    logger.info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env, shell=False)
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

def get_workflow_logs(repo, run_id):
    logger.info(f"Fetching logs for workflow run {run_id}...")
    try:
        run = repo.get_workflow_run(run_id)
        logs = []
        for job in run.get_jobs():
            if job.conclusion == "failure":
                import requests
                github_token = os.getenv("GITHUB_TOKEN")
                headers = {"Authorization": f"token {github_token}"}
                log_url = f"https://api.github.com/repos/{repo.full_name}/actions/jobs/{job.id}/logs"
                response = requests.get(log_url, headers=headers)
                if response.status_code == 200:
                    logs.append(f"Job: {job.name}\n{response.text}")
                else:
                    logger.warning(f"Failed to fetch logs for job {job.id}: {response.status_code}")
        return "\n---\n".join(logs)
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return ""

def scan_for_errors(logs):
    errors = []
    if not logs:
        return errors
    if "500" in logs or "Internal Server Error" in logs:
        errors.append("Runtime HTTP 500 error detected.")
    if "Traceback" in logs or "Exception" in logs:
        errors.append("Stack trace or exception found in logs.")
    if "error:" in logs.lower() or "failed" in logs.lower():
        errors.append("Build or test failure detected in logs.")
    return errors

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")
    event_name = os.getenv("GITHUB_EVENT_NAME")

    if not all([github_token, repo_name, event_path]):
        logger.error("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or GITHUB_EVENT_PATH.")
        sys.exit(1)

    if not openai_api_key:
        logger.warning("OPENAI_API_KEY is not set. AI Agent Loop cannot run.")
        sys.exit(0)

    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to read or parse event file: {e}")
        sys.exit(1)

    g = Github(github_token)
    repo = g.get_repo(repo_name)
    client = OpenAI(api_key=openai_api_key)

    pr_number = None
    run_id = None
    ci_failed = False
    runtime_failed = False

    if event_name == "workflow_run":
        run_id = event_data.get("workflow_run", {}).get("id")
        if event_data.get("workflow_run", {}).get("conclusion") == "failure":
            ci_failed = True
        pull_requests = event_data.get("workflow_run", {}).get("pull_requests", [])
        if pull_requests:
            pr_number = pull_requests[0].get("number")
    elif event_name == "deployment_status":
        if event_data.get("deployment_status", {}).get("state") == "failure":
            runtime_failed = True
        ref = event_data.get("deployment", {}).get("ref")
        if ref:
            pulls = repo.get_pulls(state='open', head=f"{repo.owner.login}:{ref}")
            if pulls.totalCount > 0:
                pr_number = pulls[0].number
    elif "pull_request" in event_data:
        pr_number = event_data["pull_request"].get("number")
    elif "issue" in event_data:
        pr_number = event_data["issue"].get("number")

    if not pr_number:
        pr_number = os.getenv("PR_NUMBER")

    if not pr_number:
        logger.info("Could not determine PR number. Exiting.")
        sys.exit(0)

    pr = repo.get_pull(int(pr_number))
    logger.info(f"Processing PR #{pr_number}: {pr.title}")

    logs = ""
    if ci_failed and run_id:
        logs = get_workflow_logs(repo, run_id)

    detected_errors = scan_for_errors(logs)
    if detected_errors:
        logger.info(f"Detected errors: {detected_errors}")
        if any("500" in e or "trace" in e.lower() for e in detected_errors):
            runtime_failed = True

    comments = list(pr.get_review_comments())
    cr_comments = [c for c in comments if "coderabbit" in c.user.login.lower()]
    files_to_fix = {}
    for comment in cr_comments:
        if comment.path not in files_to_fix:
            files_to_fix[comment.path] = []
        files_to_fix[comment.path].append(comment.body)

    agent_configs = [
        {"name": "Build Failure", "file": ".ai/build-failure-agent.md", "active": ci_failed},
        {"name": "Runtime Error", "file": ".ai/runtime-error-agent.md", "active": runtime_failed},
        {"name": "CodeRabbit Review", "file": ".ai/review-fix-agent.md", "active": len(files_to_fix) > 0},
        {"name": "Test", "file": ".ai/test-agent.md", "active": True},
        {"name": "Architecture", "file": ".ai/architecture-agent.md", "active": True}
    ]

    modified_files = set()
    arch_instructions = ""
    if os.path.exists(".ai/architecture-agent.md"):
        with open(".ai/architecture-agent.md", "r") as f:
            arch_instructions = f.read()

    for agent in agent_configs:
        if not agent["active"]:
            continue
        logger.info(f"Running Agent: {agent['name']}")
        try:
            with open(agent["file"], "r") as f:
                instructions = f.read()
        except FileNotFoundError:
            logger.warning(f"Instructions for {agent['name']} not found at {agent['file']}")
            continue

        if agent["name"] in ["Build Failure", "Runtime Error"] and logs:
            identify_prompt = f"Instructions: {instructions}\nLogs:\n```\n{logs[:4000]}\n```\nIdentify file paths that need fixing. Return ONLY a comma-separated list of paths."
            files_str = call_openai_with_retry(client, "gpt-4o", [{"role": "user", "content": identify_prompt}])
            identified_files = [f.strip() for f in files_str.split(",") if f.strip() and os.path.exists(f.strip())]
            for path in identified_files:
                with open(path, "r") as f: content = f.read()
                fix_prompt = f"Instructions: {instructions}\nArch Context: {arch_instructions}\nLogs:\n```\n{logs[:4000]}\n```\nFile: {path}\nContent:\n```\n{content}\n```\nReturn ONLY FULL updated file content."
                new_content = call_openai_with_retry(client, "gpt-4o", [{"role": "user", "content": fix_prompt}])
                if new_content.startswith("```"): new_content = "\n".join(new_content.splitlines()[1:-1])
                with open(path, "w") as f: f.write(new_content)
                modified_files.add(path)
        elif agent["name"] == "CodeRabbit Review":
            for path, comment_list in files_to_fix.items():
                if not os.path.exists(path): continue
                with open(path, "r") as f: content = f.read()
                prompt = f"Instructions: {instructions}\nArch Context: {arch_instructions}\nFile: {path}\nComments: {chr(10).join(comment_list)}\nContent:\n```\n{content}\n```\nReturn ONLY FULL updated file content."
                new_content = call_openai_with_retry(client, "gpt-4o", [{"role": "user", "content": prompt}])
                if new_content.startswith("```"): new_content = "\n".join(new_content.splitlines()[1:-1])
                with open(path, "w") as f: f.write(new_content)
                modified_files.add(path)
        elif agent["name"] in ["Test", "Architecture"]:
            pr_files = [f.filename for f in pr.get_files()]
            target_files = set(pr_files) | modified_files
            for path in target_files:
                if not os.path.exists(path) or os.path.isdir(path): continue
                with open(path, "r") as f: content = f.read()
                prompt = f"Instructions: {instructions}\nArch Context: {arch_instructions}\nFile: {path}\nContent:\n```\n{content}\n```\nReturn ONLY FULL updated file content."
                new_content = call_openai_with_retry(client, "gpt-4o", [{"role": "user", "content": prompt}])
                if new_content.startswith("```"): new_content = "\n".join(new_content.splitlines()[1:-1])
                with open(path, "w") as f: f.write(new_content)
                modified_files.add(path)

    if modified_files:
        logger.info("Running verification/tests...")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        stdout, code = run_command(["python3", "-m", "pytest", "tests/"], env=env)
        if code != 0:
            logger.error(f"Tests failed after fixes. Halting.\n{stdout}")
            sys.exit(code)
        run_command(["git", "config", "user.name", "github-actions[bot]"])
        run_command(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
        for f in modified_files: run_command(["git", "add", f])
        diff_check, _ = run_command(["git", "diff", "--staged"])
        if diff_check.strip():
            msg = "AI: Auto-fix build/runtime errors and review comments"
            if ci_failed: msg = f"AI: Fix CI failure - {msg}"
            if runtime_failed: msg = f"AI: Fix runtime error - {msg}"
            run_command(["git", "commit", "-m", msg])
            run_command(["git", "push", "origin", f"HEAD:{pr.head.ref}"])
            logger.info("Changes pushed successfully.")

if __name__ == "__main__":
    main()
