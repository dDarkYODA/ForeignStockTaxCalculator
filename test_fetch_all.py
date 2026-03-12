import os
import requests
import json

def main():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}" if token else ""
    }

    url = "https://api.github.com/repos/dDarkYODA/ForeignStockTaxCalculator/pulls"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching PRs: {response.status_code}")
        print(response.text)
        return

    prs = response.json()
    for pr in prs:
        # Fetch review comments
        comments_url = f"https://api.github.com/repos/dDarkYODA/ForeignStockTaxCalculator/pulls/{pr['number']}/comments"
        comments_response = requests.get(comments_url, headers=headers)
        if comments_response.status_code != 200:
            print(f"Failed to fetch comments for PR {pr['number']}")
            continue

        comments = comments_response.json()
        print(f"PR {pr['number']} ({pr['title']}) has {len(comments)} comments.")

        for comment in comments:
            if "coderabbit" in comment.get("user", {}).get("login", "").lower():
                print(f"CodeRabbit comment in {comment['path']} at line {comment.get('line') or comment.get('original_line')}:")
                print(comment['body'])
                print("-" * 40)

if __name__ == "__main__":
    main()
