import re

with open("backend/parsers/generic_parser.py", "r") as f:
    content = f.read()

# Fix 1: _heuristic_fallback single-line ifs
content = content.replace("if 'date' in k: mapping['date'] = v; break", "if 'date' in k:\n            mapping['date'] = v\n            break")
content = content.replace("if 'type' in k or 'action' in k or 'plan' in k: mapping['transaction_type'] = v; break", "if 'type' in k or 'action' in k or 'plan' in k:\n            mapping['transaction_type'] = v\n            break")
content = content.replace("if 'symbol' in k or 'ticker' in k or 'instrument' in k or 'stock' in k or 'security' in k: mapping['symbol'] = v; break", "if 'symbol' in k or 'ticker' in k or 'instrument' in k or 'stock' in k or 'security' in k:\n            mapping['symbol'] = v\n            break")
content = content.replace("if 'share' in k or 'amount' in k or 'quantity' in k: mapping['shares'] = v; break", "if 'share' in k or 'amount' in k or 'quantity' in k:\n            mapping['shares'] = v\n            break")
content = content.replace("if 'price' in k or 'value' in k or 'cost' in k: mapping['price'] = v; break", "if 'price' in k or 'value' in k or 'cost' in k:\n            mapping['price'] = v\n            break")
content = content.replace("if 'currency' in k or 'curr' in k or 'unit' in k: mapping['currency'] = v; break", "if 'currency' in k or 'curr' in k or 'unit' in k:\n            mapping['currency'] = v\n            break")

def replace_between(text, start_str, end_str, replacement):
    start_idx = text.find(start_str)
    if start_idx == -1: return text
    end_idx = text.find(end_str, start_idx)
    if end_idx == -1: return text
    return text[:start_idx] + replacement + text[end_idx:]

replacement = """def parse_generic_with_mapping(df: pd.DataFrame, mapping: dict) -> list:
    \"\"\"
    Parses a dataframe using a provided column mapping.
    \"\"\"
    transactions = []

    cols = list(df.columns)

    date_col = mapping.get('date')
    type_col = mapping.get('transaction_type')
    shares_col = mapping.get('shares')
    price_col = mapping.get('price')
    symbol_col = mapping.get('symbol')
    currency_col = mapping.get('currency')

    missing_keys = []
    for key in ['date', 'transaction_type', 'shares', 'price', 'symbol']:
        if not mapping.get(key):
            missing_keys.append(key)
    if missing_keys:
        raise ValueError(f"Missing required standard names in mapping: {', '.join(missing_keys)}")

    missing_cols = []
    for key, val in mapping.items():
        if val and val not in cols:
            missing_cols.append(f"'{val}' (for '{key}')")
    if missing_cols:
        raise ValueError(f"Fallback defaults missing in CSV columns: {', '.join(missing_cols)}")

    """

content = replace_between(content, "def parse_generic_with_mapping", "for index, row in df.iterrows():", replacement)

with open("backend/parsers/generic_parser.py", "w") as f:
    f.write(content)
