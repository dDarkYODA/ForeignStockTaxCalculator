import re

with open("backend/parsers/fidelity_parser.py", "r") as f:
    content = f.read()

content = re.sub(
    r"if 'VEST' in action_str:\n\s*tx_type = TransactionType.RSU_VEST",
    "if 'REINVESTMENT' in action_str:\n                tx_type = TransactionType.BUY\n            elif 'VEST' in action_str:\n                tx_type = TransactionType.RSU_VEST",
    content
)

with open("backend/parsers/fidelity_parser.py", "w") as f:
    f.write(content)
