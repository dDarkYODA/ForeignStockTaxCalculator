import pandas as pd
import json
import os
from openai import OpenAI
from backend.models.transaction import Transaction

def infer_schema(file_path: str) -> dict:
    df = pd.read_csv(file_path, nrows=20)
    csv_sample = df.to_csv(index=False)

    prompt = f"""
    Given the following CSV sample of stock transactions, map the columns to these standard names:
    date, transaction_type, shares, price, symbol, currency

    Return a JSON object with the standard names as keys and the CSV column names as values.
    Only return valid JSON, nothing else.

    Sample:
    {csv_sample}
    """

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

    # Normally we'd call the AI, but for offline testing/safety we mock it if no key
    if os.environ.get("OPENAI_API_KEY"):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {}
    else:
        # Better fallback mapping check logic using column contents
        cols = list(df.columns)
        mapping = {}
        for c in cols:
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
        return {
            "date": mapping.get("date", cols[0] if len(cols) > 0 else "Date"),
            "transaction_type": mapping.get("transaction_type", cols[1] if len(cols) > 1 else "Type"),
            "shares": mapping.get("shares", "Amount"),
            "price": mapping.get("price", "Value"),
            "symbol": mapping.get("symbol", "Ticker"),
            "currency": mapping.get("currency", "Currency")
        }

def parse(file_path: str, mapping: dict = None) -> list[Transaction]:
    if not mapping:
        mapping = infer_schema(file_path)
        
    df = pd.read_csv(file_path)
    transactions = []
    
    for _, row in df.iterrows():
        try:
            shares_key = mapping.get('shares', 'shares')
            price_key = mapping.get('price', 'price')
            if shares_key not in row or price_key not in row:
                continue
                
            shares = float(row.get(shares_key, 0))
            price = float(row.get(price_key, 0))
        except ValueError:
            continue
            
        date_key = mapping.get('date', 'date')
        if date_key not in row:
            continue
            
        t = Transaction(
            date=pd.to_datetime(row[date_key]).date(),
            transaction_type=row.get(mapping.get('transaction_type', 'transaction_type'), 'UNKNOWN'),
            symbol=row.get(mapping.get('symbol', 'symbol'), 'UNKNOWN'),
            shares=shares,
            price=price,
            currency=row.get(mapping.get('currency', 'currency'), 'USD'),
            broker='Unknown'
        )
        transactions.append(t)
    return transactions
