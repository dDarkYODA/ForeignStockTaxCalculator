with open('tests/test_generic_parser.py', 'r') as f:
    content = f.read()

if 'import pytest' not in content:
    content = 'import pytest\n' + content

    with open('tests/test_generic_parser.py', 'w') as f:
        f.write(content)
