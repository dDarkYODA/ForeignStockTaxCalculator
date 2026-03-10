with open("tests/test_generic_parser.py", "r") as f:
    content = f.read()

content = content.replace("        df = pd.read_csv(temp_file)\n            transactions = parse(df, mapping)", "        df = pd.read_csv(temp_file)\n        transactions = parse(df, mapping)")

content = content.replace("        df = pd.read_csv(temp_file)\n            mapping = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))\n            transactions = parse(df, mapping)", "        df = pd.read_csv(temp_file)\n        mapping = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))\n        transactions = parse(df, mapping)")

content = content.replace("        df = pd.read_csv(temp_file)\n        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))", "        df = pd.read_csv(temp_file)\n        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient=\"records\"))")

with open("tests/test_generic_parser.py", "w") as f:
    f.write(content)
