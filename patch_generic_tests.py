import re

with open("tests/test_generic_parser.py", "r") as f:
    content = f.read()

if 'import pandas as pd' not in content:
    content = 'import pandas as pd\n' + content

# Fix infer_schema calls
content = re.sub(r'schema = infer_schema\(temp_file\)',
                 'df = pd.read_csv(temp_file)\n        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))',
                 content)

# For tests that just call `transactions = parse(temp_file)`, we should also infer schema
# We can replace it with df = pd.read_csv(temp_file); mapping = infer_schema(...); parse(df, mapping)
content = re.sub(r'transactions = parse\(temp_file\)',
                 'df = pd.read_csv(temp_file)\n            mapping = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))\n            transactions = parse(df, mapping)',
                 content)

# For `transactions = parse(temp_file, mapping=mapping)`, it should be `parse(df, mapping)`
content = re.sub(r'transactions = parse\(temp_file, mapping=mapping\)',
                 'df = pd.read_csv(temp_file)\n            transactions = parse(df, mapping)',
                 content)

with open("tests/test_generic_parser.py", "w") as f:
    f.write(content)
