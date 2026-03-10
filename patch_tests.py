import re

with open("tests/test_main.py", "r") as f:
    content = f.read()

content = content.replace('assert "status" in data', 'assert "message" in data')
content = content.replace('assert data["status"] == "ok"', 'assert data["message"] == "Welcome to the Foreign Stock Tax Calculator API"')

with open("tests/test_main.py", "w") as f:
    f.write(content)
