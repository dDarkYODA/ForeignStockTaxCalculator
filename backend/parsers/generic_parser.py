import logging
import pandas as pd
import json
import os
from openai import OpenAI
from backend.models.schema import TransactionType

logger = logging.getLogger(__name__)

def infer_schema_with_ai(header_row, sample_rows=None):
    if isinstance(header_row, str) and sample_rows is None:
        df = pd.read_csv(header_row)
        header_row = list(df.columns)
        sample_rows = df.head(20).to_dict(orient="records")
    """
    Sends the header row and first 20 rows to an AI model
    to infer column mappings.
    """
    csv_sample = f"Header: {header_row}\nSample Data:\n{sample_rows}"
    prompt = f"""
    You are an expert at parsing financial CSV files.
    Here is the CSV sample:
    
    {csv_sample}
    
    Here is the header row and a sample of the first few rows of a stock transaction file.

    Header: {header_row}
    Sample Data:
    {sample_rows}

    Identify which columns correspond to the following standard fields:
    - date (transaction date)
    - transaction_type (action, plan type, etc.)
    - shares (quantity, units, etc.)
    - price (grant price, execution price, etc.)
    - symbol (ticker, security, etc.)
    - currency (USD, INR, etc. - might not exist, use null if not found)

    Return ONLY a valid JSON object mapping the standard field names to the EXACT column names found in the header.
    Example output format:
    {{
        "date": "Transaction Date",
        "transaction_type": "Action",
        "shares": "Quantity",
        "price": "Price",
        "symbol": "Symbol",
        "currency": "Currency"
    }}
    Do not include any markdown formatting or extra text.
    """
    try:
        if os.environ.get("OPENAI_API_KEY"):
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o", # Replace with appropriate model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)

        else:
            return _heuristic_fallback(header_row)
    except Exception:
        logger.error("AI schema inference failed")
        return _heuristic_fallback(header_row)

def _heuristic_fallback(header_row):
    mapping = {}
    lower_headers = {str(h).lower(): h for h in header_row}

    # Date
    for k, v in lower_headers.items():
        if 'date' in k:
            mapping['date'] = v
            break

    # Transaction Type
    for k, v in lower_headers.items():
        if 'type' in k or 'action' in k or 'plan' in k:
            mapping['transaction_type'] = v
            break

    # Symbol
    for k, v in lower_headers.items():
        if 'symbol' in k or 'ticker' in k or 'instrument' in k or 'stock' in k or 'security' in k:
            mapping['symbol'] = v
            break

    # Shares
    for k, v in lower_headers.items():
        if 'share' in k or 'amount' in k or 'quantity' in k:
            mapping['shares'] = v
            break

    # Price
    for k, v in lower_headers.items():
        if 'price' in k or 'value' in k or 'cost' in k:
            mapping['price'] = v
            break

    # Currency
    # First pass: look for exact matches
    for k, v in lower_headers.items():
        if k == 'currency' or k == 'curr' or k == 'unit':
            mapping['currency'] = v
            break

    # Second pass: look for substrings if exact match not found
    if 'currency' not in mapping:
        for k, v in lower_headers.items():
            if 'currency' in k or ' curr' in k or ' unit' in k:
                mapping['currency'] = v
                break

    return mapping


def parse_generic_with_mapping(df, mapping=None) -> list:
    if isinstance(df, str):
        df = pd.read_csv(df)
    if mapping is None:
        mapping = infer_schema_with_ai(list(df.columns), df.head(20).to_dict(orient="records"))
    """
    Parses a dataframe using a provided column mapping.
    """
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

    for index, row in df.iterrows():
        try:

            try:
                dt = pd.to_datetime(str(row[date_col])).date()
            except:
                continue

            type_str = str(row[type_col]).upper()
            if 'VEST' in type_str:
                tx_type = TransactionType.RSU_VEST
            elif 'PURCHASE' in type_str or 'BUY' in type_str:
                tx_type = TransactionType.BUY
            elif 'SELL' in type_str or 'SALE' in type_str:
                tx_type = TransactionType.SELL
            else:
                continue # Skip unknown types

            if pd.isna(row[shares_col]) or pd.isna(row[price_col]) or pd.isna(row[symbol_col]):
                continue

            if str(row[shares_col]).strip() == "" or str(row[price_col]).strip() == "" or str(row[symbol_col]).strip() == "":
                continue

            shares = float(str(row[shares_col]).replace(',', ''))

            price_str = str(row[price_col]).replace('$', '').replace(',', '')
            price = float(price_str) if price_str.strip() else 0.0

            symbol = str(row[symbol_col]).strip()
            if not symbol:
                continue

            currency = str(row[currency_col]).strip() if currency_col and not pd.isna(row[currency_col]) else "USD"

            transactions.append({
                "date": dt,
                "transaction_type": tx_type,
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "currency": currency,
                "broker": "Generic"
            })
        except Exception:
            logger.error("Error parsing row in generic statement")
            continue

    return transactions
