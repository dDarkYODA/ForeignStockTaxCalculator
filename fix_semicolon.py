import re

with open("tests/test_generic_parser.py", "r") as f:
    content = f.read()

content = content.replace("schema = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\")); transactions = parse(df, mapping=schema)", "schema = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))\n        transactions = parse(df, mapping=schema)")

content = content.replace('            assert False, "Expected ValueError"', '            import pytest; pytest.fail("Expected ValueError")')

with open("tests/test_generic_parser.py", "w") as f:
    f.write(content)
