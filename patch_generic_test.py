import re

with open("tests/test_generic_parser.py", "r") as f:
    content = f.read()

content = re.sub(r"df = pd\.read_csv\(temp_file\)\n        schema = infer_schema\(list\(df\.columns\), df\.head\(20\)\.to_dict\(orient=\"records\"\)\); transactions = parse\(df, mapping=schema\)", r"df = pd.read_csv(temp_file)\n        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))\n        transactions = parse(df, mapping=schema)", content)


with open("tests/test_generic_parser.py", "w") as f:
    f.write(content)
