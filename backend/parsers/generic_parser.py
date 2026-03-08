import pandas as pd
import json
import os
from openai import OpenAI
<<<<<<< HEAD
from backend.services.braintrust_client import log_ai_call
from backend.models.transaction import Transaction

def infer_schema(file_path: str) -> dict:
    try:
        df = pd.read_csv(file_path, nrows=20)
    except Exception:
        # If it fails to read standard comma CSV, try skipping bad lines or other separators
        try:
            df = pd.read_csv(file_path, nrows=20, on_bad_lines='skip')
        except Exception:
            # Absolute fallback
            return {}

    result = {}
    used_fallback = False

    # Normally we'd call the AI, but for offline testing/safety we mock it if no key
    if os.environ.get("OPENAI_API_KEY"):
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        csv_sample = df.to_csv(index=False)
        prompt = f"""
        Given the following CSV sample of stock transactions, map the columns to these standard names:
        date, transaction_type, shares, price, symbol, currency

        Return a JSON object with the standard names as keys and the CSV column names as values.
        Only return valid JSON, nothing else.

        Sample:
        {csv_sample}
        """
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            result = json.loads(response.choices[0].message.content)
        except Exception:
            used_fallback = True
    else:
        used_fallback = True
        prompt = "Infer schema from this CSV snippet (rule-based fallback used)."

    if used_fallback:
        # Better fallback mapping check logic using column contents
        cols = list(df.columns)
        mapping = {}

        # Clean column names by stripping whitespace for matching
        cleaned_cols = [str(c).strip() for c in cols]

        for c in cleaned_cols:
            lower_c = c.lower()
            if 'date' in lower_c and 'date' not in mapping:
                mapping['date'] = c
            elif 'plan' in lower_c or 'type' in lower_c or 'action' in lower_c:
                mapping['transaction_type'] = c
            elif 'instrument' in lower_c or 'symbol' in lower_c or 'security' in lower_c or 'ticker' in lower_c:
                mapping['symbol'] = c
            elif 'quantity' in lower_c or 'shares' in lower_c or 'amount' in lower_c:
                mapping['shares'] = c
            elif 'cost basis' in lower_c and 'unit' not in lower_c:
                mapping['price'] = c
            elif 'price' in lower_c or 'value' in lower_c:
                if 'price' not in mapping:
                    mapping['price'] = c
            elif 'unit' in lower_c or 'currency' in lower_c:
                mapping['currency'] = c

        # Fill missing with safe defaults that exist or won't crash directly
        result = {
            "date": mapping.get("date", cleaned_cols[0] if len(cleaned_cols) > 0 else "Date"),
            "transaction_type": mapping.get("transaction_type", cleaned_cols[1] if len(cleaned_cols) > 1 else "Type"),
            "shares": mapping.get("shares", "Amount"),
            "price": mapping.get("price", "Value"),
            "symbol": mapping.get("symbol", "Ticker"),
            "currency": mapping.get("currency", "Currency")
        }

        # Check for missing fallbacks
        for key, val in result.items():
            if val not in cols and val not in cleaned_cols:
                print(f"Warning: Fallback default '{val}' for standard name '{key}' is missing in the CSV columns.")

    # Log to braintrust
    try:
        sample_data = df.head(5).to_csv(index=False)
        log_ai_call(
            input_sample=sample_data,
            prompt=prompt,
            response=result,
            metadata={"task": "schema_inference", "used_fallback": used_fallback}
        )
    except Exception as e:
        print(f"Braintrust logging failed: {e}")

    return result

def parse(file_path: str, mapping: dict = None) -> list[Transaction]:
    if not mapping:
        mapping = infer_schema(file_path)

    try:
        # read_csv with on_bad_lines skip to prevent breaking on malformed rows
        df = pd.read_csv(file_path, on_bad_lines='skip')
    except Exception:
        return []

    # Strip whitespace from columns
    df.columns = [str(c).strip() for c in df.columns]

    transactions = []

    for _, row in df.iterrows():
        try:
            shares_key = mapping.get('shares', 'shares')
            price_key = mapping.get('price', 'price')
            if shares_key not in row or price_key not in row:
                continue

            # clean up strings that might be inside numerical columns
            s_val = str(row.get(shares_key, '0')).replace(',', '')
            p_val = str(row.get(price_key, '0')).replace(',', '')
            shares = float(s_val)
            price = float(p_val)
        except ValueError:
            continue

        date_key = mapping.get('date', 'date')
        if date_key not in row:
            continue

        # Parse date safely
        try:
            dt = pd.to_datetime(str(row[date_key]).strip()).date()
        except Exception:
            continue

        t = Transaction(
            date=dt,
            transaction_type=str(row.get(mapping.get('transaction_type', 'transaction_type'), 'UNKNOWN')).strip(),
            symbol=str(row.get(mapping.get('symbol', 'symbol'), 'UNKNOWN')).strip(),
            shares=shares,
            price=price,
            currency=str(row.get(mapping.get('currency', 'currency'), 'USD')).strip(),
            broker='Unknown'
        )
        transactions.append(t)
=======
from models.schema import TransactionType

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy_key"))

def infer_schema_with_ai(header_row, sample_rows):
    """
    Sends the header row and first 20 rows to an AI model
    to infer column mappings.
    """
    prompt = f"""
    You are an expert at parsing financial CSV files.
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
        response = client.chat.completions.create(
            model="gpt-4o", # Replace with appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling AI: {e}")
        return {}

def parse_generic_with_mapping(df: pd.DataFrame, mapping: dict) -> list:
    """
    Parses a dataframe using a provided column mapping.
    """
    transactions = []

    for index, row in df.iterrows():
        try:
            date_col = mapping.get('date')
            type_col = mapping.get('transaction_type')
            shares_col = mapping.get('shares')
            price_col = mapping.get('price')
            symbol_col = mapping.get('symbol')
            currency_col = mapping.get('currency')

            # Require minimum fields
            if not all([date_col, type_col, shares_col, price_col, symbol_col]):
                continue

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

            shares = float(str(row[shares_col]).replace(',', ''))

            price_str = str(row[price_col]).replace('$', '').replace(',', '')
            price = float(price_str) if price_str.strip() else 0.0

            symbol = str(row[symbol_col]).strip()

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

>>>>>>> origin/main
    return transactions
