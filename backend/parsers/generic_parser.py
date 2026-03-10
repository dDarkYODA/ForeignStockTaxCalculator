import pandas as pd
import json
import os
from openai import OpenAI
from backend.models.schema import TransactionType

def infer_schema_with_ai(header_row, sample_rows):
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
            return fallback_infer(header_row)
    except Exception as e:
        print(f"Error calling AI: {e}")
        return fallback_infer(header_row)

def fallback_infer(header_row):
    mapping = {}
    for col in header_row:
        c = str(col).lower()
        if 'date' in c and not mapping.get('date'):
            mapping['date'] = col
        elif ('type' in c or 'action' in c) and not mapping.get('transaction_type'):
            mapping['transaction_type'] = col
        elif ('share' in c or 'qty' in c or 'quantity' in c or 'amount' in c) and not mapping.get('shares'):
            mapping['shares'] = col
        elif ('price' in c or 'cost' in c or 'value' in c) and not mapping.get('price'):
            mapping['price'] = col
        elif ('symbol' in c or 'ticker' in c or 'security' in c or 'instrument' in c) and not mapping.get('symbol'):
            mapping['symbol'] = col
        elif 'curr' in c and not mapping.get('currency'):
            mapping['currency'] = col
    return mapping


def parse_generic_with_mapping(df: pd.DataFrame, mapping: dict) -> list:
    """
    Parses a dataframe using a provided column mapping.
    """
    transactions = []
    
    cols = list(df.columns)
    for key, val in mapping.items():
        if val and val not in cols:
            print(f"Warning: Fallback default '{val}' for standard name '{key}' is missing in the CSV columns.")

    date_col = mapping.get('date')
    type_col = mapping.get('transaction_type')
    shares_col = mapping.get('shares')
    price_col = mapping.get('price')
    symbol_col = mapping.get('symbol')
    currency_col = mapping.get('currency')

    # Require minimum fields
    if not all([date_col, type_col, shares_col, price_col, symbol_col]):
        raise ValueError("Missing required fields in mapping")

    for col in [date_col, type_col, shares_col, price_col, symbol_col]:
        if col not in df.columns:
            raise ValueError(f"Mapped column '{col}' not found in data")

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
        except Exception as e:
            print(f"Error parsing generic row {index}: {e}")
            continue

    return transactions
