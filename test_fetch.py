import os
import requests
import json

def main():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}" if token else ""
    }

    # We want to find the PR that matches our current branch.
    # What branch are we on?
    import subprocess
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    print(f"Current branch: {branch}")

    url = "https://api.github.com/repos/dDarkYODA/ForeignStockTaxCalculator/pulls"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching PRs: {response.status_code}")
        print(response.text)
        return

    prs = response.json()
    for pr in prs:
        print(f"PR {pr['number']}: {pr['title']} (branch: {pr['head']['ref']})")
        if pr['head']['ref'] == branch:
            print(f"Found PR {pr['number']} for current branch!")

            # Fetch review comments
            comments_url = f"https://api.github.com/repos/dDarkYODA/ForeignStockTaxCalculator/pulls/{pr['number']}/comments"
            comments_response = requests.get(comments_url, headers=headers)
            comments = comments_response.json()

            for comment in comments:
                if "coderabbit" in comment.get("user", {}).get("login", "").lower():
                    print(f"CodeRabbit comment in {comment['path']} at line {comment.get('line') or comment.get('original_line')}:")
                    print(comment['body'])
                    print("-" * 40)

if __name__ == "__main__":
    main()
