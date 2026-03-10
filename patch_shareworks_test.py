import re

with open("tests/test_shareworks_parser.py", "r") as f:
    content = f.read()

replacement = """df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 4
        plan_types = [t['transaction_type'].value for t in transactions]
        assert plan_types.count('RSU_VEST') == 1
        assert plan_types.count('ESPP_PURCHASE') == 2
        assert plan_types.count('SELL') == 1"""

content = re.sub(r"df = pd\.read_csv\(temp_file\)\n        transactions = parse\(df\)\n\n        assert len\(transactions\) == 4\n        plan_types = \[t\['transaction_type'\] for t in transactions\]\n        plan_types = \[p\.value for p in plan_types\]; assert 'RSU_VEST' in plan_types\n        assert 'ESPP_PURCHASE' in plan_types\n        assert 'RSU_VEST' in plan_types\n        assert 'SELL' in plan_types", replacement, content)


content = re.sub(r"def test_parse_negative_values\(\):\n    \"\"\"Test parsing handles negative values \(edge case for returns/corrections\)\"\"\"\n    with tempfile\.NamedTemporaryFile\(mode='w', suffix='\.csv', delete=False\) as f:\n        writer = csv\.writer\(f\)\n        writer\.writerow\(\['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'\]\)\n        writer\.writerow\(\['2024-03-01', 'CORRECTION', 'AMD', '-5', '180\.00'\]\)\n        temp_file = f\.name\n\n    try:\n        df = pd\.read_csv\(temp_file\)\n        transactions = parse\(df\)\n\n        assert len\(transactions\) == 1\n        assert transactions\[0\]\['shares'\] == -5\.0\n    finally:\n        os\.unlink\(temp_file\)", r"""def test_parse_negative_values():
    \"\"\"Test parsing handles negative values (edge case for returns/corrections)\"\"\"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2024-03-01', 'CORRECTION', 'AMD', '-5', '180.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        # CORRECTION is now skipped
        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)""", content)

with open("tests/test_shareworks_parser.py", "w") as f:
    f.write(content)
