import sys

def main():
    content = ""
    with open("backend/services/tax_engine.py", "r") as f:
        content = f.read()

    old_lot = """
            lot = Lot(
                user_id=user_id,
                date=txn.date,
                symbol=txn.symbol,
                shares=txn.shares,
                price=txn.price,
                cost_inr=cost_inr,
                available_shares=txn.shares
            )
            # Add currency dynamically if needed, schema currently doesn't have it on Lot but let's assume it inherits or defaults to USD.
            lot.currency = txn.currency
"""

    new_lot = """
            lot = Lot(
                user_id=user_id,
                date=txn.date,
                symbol=txn.symbol,
                shares=txn.shares,
                price=txn.price,
                cost_inr=cost_inr,
                available_shares=txn.shares,
                currency=txn.currency
            )
"""

    content = content.replace(old_lot, new_lot)

    with open("backend/services/tax_engine.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
