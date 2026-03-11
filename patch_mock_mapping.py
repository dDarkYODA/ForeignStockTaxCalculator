import re

with open("tests/test_generic_parser.py", "r") as f:
    content = f.read()

# Make the mock mapping dynamic to map exactly what's in the df to fix the ValueError
mock_mapping_new = """mapping = {
            'date': next((c for c in df.columns if 'date' in c.lower()), None),
            'transaction_type': next((c for c in df.columns if 'action' in c.lower() or 'type' in c.lower()), None),
            'symbol': next((c for c in df.columns if 'symbol' in c.lower() or 'ticker' in c.lower() or 'security' in c.lower()), None),
            'shares': next((c for c in df.columns if 'share' in c.lower() or 'quantity' in c.lower() or 'amount' in c.lower()), None),
            'price': next((c for c in df.columns if 'price' in c.lower() or 'value' in c.lower() or 'cost' in c.lower()), None),
            'currency': next((c for c in df.columns if 'curr' in c.lower()), None)
        }
"""

content = re.sub(
    r'mapping = \{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}\n\s*if \'action\' not in df\.columns[\s\S]*?(?=transactions = parse)',
    mock_mapping_new + "        ",
    content
)

with open("tests/test_generic_parser.py", "w") as f:
    f.write(content)
