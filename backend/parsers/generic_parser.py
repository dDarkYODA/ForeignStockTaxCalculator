import pandas as pd
import json
import os
from openai import OpenAI
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
            
    # Fill missing with safe defaults
    return {
        "date": mapping.get("date", cleaned_cols[0] if len(cleaned_cols) > 0 else "Date"),
        "transaction_type": mapping.get("transaction_type", cleaned_cols[1] if len(cleaned_cols) > 1 else "Type"),
        "shares": mapping.get("shares", "Amount"),
        "price": mapping.get("price", "Value"),
        "symbol": mapping.get("symbol", "Ticker"),
        "currency": mapping.get("currency", "Currency")
    }

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
    return transactions
