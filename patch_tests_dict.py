import re
import glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace object attributes with dictionary access
    # e.g., transactions[0].date -> transactions[0]['date']
    content = re.sub(r'(transactions\[\d+\])\.([a-zA-Z_]+)', r"\1['\2']", content)

    # Replace list comprehensions
    # e.g., [t.symbol for t in transactions] -> [t['symbol'] for t in transactions]
    content = re.sub(r't\.([a-zA-Z_]+)\s+for\s+t', r"t['\1'] for t", content)

    # Also handle assert t.symbol
    content = re.sub(r'assert t\.([a-zA-Z_]+)', r"assert t['\1']", content)

    with open(filepath, 'w') as f:
        f.write(content)

patch_file("tests/test_shareworks_parser.py")
patch_file("tests/test_fidelity_parser.py")
patch_file("tests/test_generic_parser.py")
