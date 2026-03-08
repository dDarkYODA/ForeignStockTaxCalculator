import pandas as pd
from backend.models.transaction import Transaction

def parse(file_path: str) -> list[Transaction]:
    """
    Parse a CSV export of Shareworks transactions into a list of Transaction objects.
    
    Parameters:
        file_path (str): Path to a CSV file containing Shareworks transactions. The CSV must include the columns
            'Transaction Date', 'Plan Type', 'Symbol', 'Shares', and 'Price'. 'Transaction Date' will be parsed
            as a datetime and 'Shares' and 'Price' will be converted to numeric; rows with invalid numeric values
            for 'Shares' or 'Price' are skipped.
    
    Returns:
        list[Transaction]: A list of Transaction objects with `date` set to the date portion of 'Transaction Date',
            `transaction_type` from 'Plan Type', `symbol` from 'Symbol', numeric `shares` and `price`, `currency`
            set to 'USD', and `broker` set to 'Shareworks'.
    """
    df = pd.read_csv(file_path)
    
    # Pre-process columns to optimize the loop
    # 1. Vectorized date conversion
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])

    # 2. Vectorized numeric conversion with error handling
    # Convert to numeric, then drop rows with NaN in Shares or Price to match original behavior (continue)
    df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['Shares', 'Price'])

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
