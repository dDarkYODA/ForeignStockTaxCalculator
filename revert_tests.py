import re

for filepath in ["tests/test_shareworks_parser.py", "tests/test_fidelity_parser.py", "tests/test_generic_parser.py"]:
    with open(filepath, 'r') as f:
        content = f.read()

    # Revert dictionary access back to object attributes
    content = re.sub(r'(transactions\[\d+\])\[\'([a-zA-Z_]+)\'\]', r"\1.\2", content)
    content = re.sub(r't\[\'([a-zA-Z_]+)\'\]\s+for\s+t', r"t.\1 for t", content)
    content = re.sub(r'assert t\[\'([a-zA-Z_]+)\'\]', r"assert t.\1", content)

    with open(filepath, 'w') as f:
        f.write(content)
