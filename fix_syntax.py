import re

for filename in ["tests/test_generic_parser.py", "tests/test_shareworks_parser.py"]:
    with open(filename, "r") as f:
        content = f.read()

    content = content.replace('\\"', '"')

    with open(filename, "w") as f:
        f.write(content)
