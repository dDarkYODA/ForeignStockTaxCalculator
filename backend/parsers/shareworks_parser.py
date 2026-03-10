import pandas as pd
from datetime import datetime
from backend.models.schema import TransactionType

def parse_shareworks(df: pd.DataFrame) -> list:
    transactions = []

    # Typical mappings for Morgan Stanley Shareworks
    # Transaction Date -> date
    # Plan Type -> transaction_type
    # Shares -> shares
    # Price -> price
    # Symbol -> symbol

    # Try to clean column names to make it robust
    df.columns = [str(c).strip() for c in df.columns]

    # Look for expected columns
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    type_col = next((c for c in df.columns if 'plan type' in c.lower() or 'type' in c.lower()), None)
    shares_col = next((c for c in df.columns if 'shares' in c.lower()), None)
    price_col = next((c for c in df.columns if 'price' in c.lower()), None)
    symbol_col = next((c for c in df.columns if 'symbol' in c.lower()), None)

    if not all([date_col, type_col, shares_col, price_col, symbol_col]):
        raise ValueError("Missing required columns for Shareworks parser")

    for index, row in df.iterrows():
        try:
            # Handle date parsing flexibly
            date_str = str(row[date_col])
            try:
                dt = pd.to_datetime(date_str).date()
            except:
                continue

            type_str = str(row[type_col]).upper()
            if 'VEST' in type_str or 'RSU' in type_str or 'OPTION' in type_str:
                tx_type = TransactionType.RSU_VEST
            elif 'PURCHASE' in type_str or 'ESPP' in type_str:
                tx_type = TransactionType.ESPP_PURCHASE
            elif 'SELL' in type_str or 'SALE' in type_str:
                tx_type = TransactionType.SELL
            elif 'BUY' in type_str:
                tx_type = TransactionType.BUY
            else:
                continue # Skip unknown types

            if pd.isna(row[shares_col]) or pd.isna(row[price_col]) or pd.isna(row[symbol_col]):
                continue

            qty_str = str(row[shares_col]).replace(',', '').strip()
            price_str = str(row[price_col]).replace('$', '').replace(',', '').strip()
            symbol = str(row[symbol_col]).strip()

            if not qty_str or not price_str or not symbol:
                continue

            shares = float(qty_str)
            price = float(price_str)

            transactions.append({
                "date": dt,
                "transaction_type": tx_type,
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "currency": "USD", # Default to USD for shareworks typically
                "broker": "Shareworks"
            })
        except Exception as e:
            # Skip rows that can't be parsed
            print(f"Error parsing row {index}: {e}")
            continue

    return transactions
