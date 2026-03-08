import pandas as pd
from backend.models.transaction import Transaction

def parse(file_path: str) -> list[Transaction]:
    df = pd.read_csv(file_path)
    transactions = []
    
    for _, row in df.iterrows():
        try:
            shares = float(row.get('Quantity', 0))
            price = float(row.get('Price', 0))
        except ValueError:
            continue

        t = Transaction(
            date=pd.to_datetime(row['Date']).date(),
            transaction_type=row['Action'],
            symbol=row['Security'],
            shares=shares,
            price=price,
            currency='USD',
            broker='Fidelity'
        )
        transactions.append(t)
    return transactions
