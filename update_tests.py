import re

with open("tests/test_fidelity_parser.py", "r") as f:
    content = f.read()

# Fix the test_parse_negative_quantity
replacement = """def test_parse_negative_quantity():
    \"\"\"Test parsing handles negative quantity (edge case for corrections)\"\"\"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2024-03-01', 'Adjustment', 'AMD', '-5', '180.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)"""

content = re.sub(
    r"def test_parse_negative_quantity\(\):.*?finally:\n        os\.unlink\(temp_file\)",
    replacement,
    content,
    flags=re.DOTALL
)

with open("tests/test_fidelity_parser.py", "w") as f:
    f.write(content)

with open("backend/parsers/fidelity_parser.py", "r") as f:
    content = f.read()

content = content.replace("""            if 'VEST' in action_str:
                tx_type = TransactionType.RSU_VEST
            elif 'PURCHASE' in action_str or 'BUY' in action_str or 'REINVESTMENT' in action_str:
                tx_type = TransactionType.BUY
            elif 'SELL' in action_str or 'SALE' in action_str:""", """            if 'REINVESTMENT' in action_str:
                tx_type = TransactionType.BUY
            elif 'VEST' in action_str:
                tx_type = TransactionType.RSU_VEST
            elif 'PURCHASE' in action_str or 'BUY' in action_str:
                tx_type = TransactionType.BUY
            elif 'SELL' in action_str or 'SALE' in action_str:""")

with open("backend/parsers/fidelity_parser.py", "w") as f:
    f.write(content)
