import re

with open('tests/test_shareworks_parser.py', 'r') as f:
    content = f.read()

replacement = """        assert len(transactions) == 4

        # Verify specific transactions mapped correctly
        option_tx = next(t for t in transactions if t['shares'] == 15)
        assert option_tx['transaction_type'].value == 'OPTION_EXERCISE'

        espp_tx = next(t for t in transactions if t['shares'] == 5)
        assert espp_tx['transaction_type'].value == 'ESPP_PURCHASE'

        plan_types = [t['transaction_type'].value for t in transactions]
        assert plan_types.count('RSU_VEST') == 1
        assert plan_types.count('ESPP_PURCHASE') == 1
        assert plan_types.count('OPTION_EXERCISE') == 1
        assert plan_types.count('SELL') == 1"""

content = re.sub(
    r"        assert len\(transactions\) == 4\n        plan_types = \[t\['transaction_type'\]\.value for t in transactions\]\n        assert plan_types\.count\('RSU_VEST'\) == 1\n        assert plan_types\.count\('ESPP_PURCHASE'\) == 1\n        assert plan_types\.count\('OPTION_EXERCISE'\) == 1\n        assert plan_types\.count\('SELL'\) == 1",
    replacement,
    content
)

with open('tests/test_shareworks_parser.py', 'w') as f:
    f.write(content)
