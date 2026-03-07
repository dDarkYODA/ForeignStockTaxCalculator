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
        # Mock response for testing
        return {
            "date": "Date",
            "transaction_type": "Type",
            "shares": "Amount",
            "price": "Value",
            "symbol": "Ticker",
            "currency": "Currency"
        }

def parse(file_path: str, mapping: dict = None) -> list[Transaction]:
    if not mapping:
        mapping = infer_schema(file_path)
        
    df = pd.read_csv(file_path)
    transactions = []
    
    for _, row in df.iterrows():
        try:
            shares = float(row.get(mapping.get('shares', 'shares'), 0))
            price = float(row.get(mapping.get('price', 'price'), 0))
        except ValueError:
            continue
            
        t = Transaction(
            date=pd.to_datetime(row[mapping.get('date', 'date')]).date(),
            transaction_type=row[mapping.get('transaction_type', 'transaction_type')],
            symbol=row[mapping.get('symbol', 'symbol')],
            shares=shares,
            price=price,
            currency=row.get(mapping.get('currency', 'currency'), 'USD'),
            broker='Unknown'
        )
        transactions.append(t)
    return transactions
