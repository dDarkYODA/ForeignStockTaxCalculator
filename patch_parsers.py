import re

for filename, func_name in [
    ("backend/parsers/shareworks_parser.py", "parse_shareworks"),
    ("backend/parsers/fidelity_parser.py", "parse_fidelity"),
    ("backend/parsers/generic_parser.py", "parse_generic_with_mapping"),
    ("backend/parsers/generic_parser.py", "infer_schema_with_ai")
]:
    with open(filename, "r") as f:
        content = f.read()

    if func_name == "parse_shareworks":
        content = re.sub(r'def parse_shareworks\(df: pd\.DataFrame\) -> list:', 'def parse_shareworks(df) -> list:\n    if isinstance(df, str):\n        df = pd.read_csv(df)', content)
    elif func_name == "parse_fidelity":
        content = re.sub(r'def parse_fidelity\(df: pd\.DataFrame\) -> list:', 'def parse_fidelity(df) -> list:\n    if isinstance(df, str):\n        df = pd.read_csv(df)', content)
    elif func_name == "parse_generic_with_mapping":
        content = re.sub(r'def parse_generic_with_mapping\(df: pd\.DataFrame, mapping: dict\) -> list:', 'def parse_generic_with_mapping(df, mapping=None) -> list:\n    if isinstance(df, str):\n        df = pd.read_csv(df)\n    if mapping is None:\n        mapping = infer_schema_with_ai(list(df.columns), df.head(20).to_dict(orient="records"))', content)
    elif func_name == "infer_schema_with_ai":
        content = re.sub(r'def infer_schema_with_ai\(header_row, sample_rows\):', 'def infer_schema_with_ai(header_row, sample_rows=None):\n    if isinstance(header_row, str) and sample_rows is None:\n        df = pd.read_csv(header_row)\n        header_row = list(df.columns)\n        sample_rows = df.head(20).to_dict(orient="records")', content)

    with open(filename, "w") as f:
        f.write(content)

with open("backend/parsers/generic_parser.py", "r") as f:
    content = f.read()
if "import pandas as pd" not in content:
    content = "import pandas as pd\n" + content
with open("backend/parsers/generic_parser.py", "w") as f:
    f.write(content)
