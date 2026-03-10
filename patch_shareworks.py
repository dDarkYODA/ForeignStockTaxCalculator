with open("backend/parsers/shareworks_parser.py", "r") as f:
    content = f.read()

content = content.replace(
    "elif 'SELL' in type_str or 'SALE' in type_str or 'CORRECTION' in type_str:\n                tx_type = TransactionType.SELL",
    "elif 'SELL' in type_str or 'SALE' in type_str:\n                tx_type = TransactionType.SELL"
)

with open("backend/parsers/shareworks_parser.py", "w") as f:
    f.write(content)
