import pandas as pd
from datetime import datetime
from backend.models.schema import TransactionType

def parse_fidelity(df: pd.DataFrame) -> list:
    transactions = []

    # Typical mappings for Fidelity
    # Date -> date
    # Action -> transaction_type
    # Quantity -> shares
    # Price -> price
    # Security -> symbol

    # Try to clean column names to make it robust
    df.columns = [str(c).strip() for c in df.columns]

    # Look for expected columns
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    action_col = next((c for c in df.columns if 'action' in c.lower()), None)
    qty_col = next((c for c in df.columns if 'quantity' in c.lower() or 'shares' in c.lower()), None)
    price_col = next((c for c in df.columns if 'price' in c.lower()), None)
    security_col = next((c for c in df.columns if 'security' in c.lower() or 'symbol' in c.lower()), None)

    if not all([date_col, action_col, qty_col, price_col, security_col]):
        raise ValueError("Missing required columns for Fidelity parser")

    for index, row in df.iterrows():
        try:
            # Handle date parsing flexibly
            date_str = str(row[date_col])
            try:
                dt = pd.to_datetime(date_str).date()
            except:
                continue

            action_str = str(row[action_col]).upper()
            if 'VEST' in action_str:
                tx_type = TransactionType.RSU_VEST
            elif 'PURCHASE' in action_str or 'BUY' in action_str:
                tx_type = TransactionType.BUY
            elif 'SELL' in action_str or 'SALE' in action_str:
                tx_type = TransactionType.SELL
            else:
                continue # Skip unknown types

            if pd.isna(row[qty_col]):
                shares = 0.0
            else:
                qty_str = str(row[qty_col]).replace(',', '')
                shares = float(qty_str) if qty_str.strip() else 0.0

            if pd.isna(row[price_col]):
                price = 0.0
            else:
                price_str = str(row[price_col]).replace('$', '').replace(',', '')
                price = float(price_str) if price_str.strip() else 0.0

            if pd.isna(row[security_col]):
                continue
            symbol = str(row[security_col]).strip()
            if not symbol: continue

            transactions.append({
                "date": dt,
                "transaction_type": tx_type,
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "currency": "USD", # Default to USD
                "broker": "Fidelity"
            })
        except Exception as e:
            print(f"Error parsing row {index}: {e}")
            continue

    return transactions
