import pandas as pd
from backend.models.transaction import Transaction

def parse(file_path: str) -> list[Transaction]:
    df = pd.read_csv(file_path)
    
    # Pre-process columns to optimize the loop
    # 1. Vectorized date conversion
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')

    # 2. Vectorized numeric conversion with error handling
    # Convert to numeric, then drop rows with NaT/NaN in Date, Shares or Price to match original behavior (continue)
    df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['Transaction Date', 'Shares', 'Price'])

    transactions = []
    # to_dict('records') is often faster for creating objects in a loop
    for row in df.to_dict('records'):
        t = Transaction(
            date=row['Transaction Date'].date(),
            transaction_type=row['Plan Type'],
            symbol=row['Symbol'],
            shares=row['Shares'],
            price=row['Price'],
            currency='USD',
            broker='Shareworks'
        )
        transactions.append(t)
    return transactions
