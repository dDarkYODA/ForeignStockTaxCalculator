import pandas as pd
from backend.models.transaction import Transaction

def parse(file_path: str) -> list[Transaction]:
    df = pd.read_csv(file_path)
    transactions = []
    
    for _, row in df.iterrows():
        # Handle cases where shares/price might be missing or empty strings
        try:
            shares = float(row.get('Shares', 0))
            price = float(row.get('Price', 0))
        except ValueError:
            continue
            
        t = Transaction(
            date=pd.to_datetime(row['Transaction Date']).date(),
            transaction_type=row['Plan Type'],
            symbol=row['Symbol'],
            shares=shares,
            price=price,
            currency='USD', # Defaulting to USD for shareworks
            broker='Shareworks'
        )
        transactions.append(t)
    return transactions
