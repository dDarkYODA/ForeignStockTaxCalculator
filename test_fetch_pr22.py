import os
import requests
import json

def main():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}" if token else ""
    }

    # Fetch review comments
    comments_url = "https://api.github.com/repos/dDarkYODA/ForeignStockTaxCalculator/pulls/22/comments"
    comments_response = requests.get(comments_url, headers=headers)
    comments = comments_response.json()

    for comment in comments:
        if "coderabbit" in comment.get("user", {}).get("login", "").lower():
            print(f"CodeRabbit comment in {comment['path']} at line {comment.get('line') or comment.get('original_line')}:")
            print(comment['body'])
            print("-" * 40)

if __name__ == "__main__":
    main()
