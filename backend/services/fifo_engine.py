<<<<<<< HEAD
from backend.models.transaction import Transaction

def match_lots(transactions: list[Transaction]) -> list[tuple[Transaction, Transaction, float]]:
    """
    Match BUY/VEST transactions with SELL transactions using FIFO.
    Returns a list of tuples: (buy_transaction, sell_transaction, matched_shares)
    """
    matches = []

    # Sort by date
    transactions = sorted(transactions, key=lambda x: x.date)

    # Track inventory (buy/vest lots)
    inventory = []

    for t in transactions:
        # Match "SELL" exactly or contain 'sell' in type to handle variants
        is_sell = (t.transaction_type == 'SELL' or 'sell' in t.transaction_type.lower())

        if not is_sell:
            inventory.append({
                'tx': t,
                'remaining': t.shares
            })
        else:
            shares_to_sell = t.shares

            # Consume inventory
            while shares_to_sell > 0 and inventory:
                lot = inventory[0]
                available = lot['remaining']

                if available <= shares_to_sell:
                    matches.append((lot['tx'], t, available))
                    shares_to_sell -= available
                    inventory.pop(0)
                else:
                    matches.append((lot['tx'], t, shares_to_sell))
                    lot['remaining'] -= shares_to_sell
                    shares_to_sell = 0

    return matches
=======
from models.schema import Lot
from sqlalchemy.orm import Session
from datetime import date
from .fx_service import fx_service

def match_sell_fifo(db: Session, user_id: str, symbol: str, shares_to_sell: float, sell_date: date, sell_price: float, sell_currency: str) -> list:
    """
    Matches a sell transaction against available lots using FIFO.
    Calculates capital gains and returns a list of resulting calculations.
    """
    results = []

    # Get available lots for this symbol, ordered by date (FIFO)
    available_lots = db.query(Lot).filter(
        Lot.user_id == user_id,
        Lot.symbol == symbol,
        Lot.available_shares > 0
    ).order_by(Lot.date).all()

    shares_remaining = shares_to_sell

    for lot in available_lots:
        if shares_remaining <= 0:
            break

        shares_matched = min(shares_remaining, lot.available_shares)

        # Calculate holding period
        months_held = (sell_date.year - lot.date.year) * 12 + sell_date.month - lot.date.month
        if sell_date.day < lot.date.day:
            months_held -= 1

        holding_type = "LTCG" if months_held > 24 else "STCG"

        # Calculate costs and gains
        # Cost INR is calculated based on the FX rate at the time of purchase
        cost_fx_rate = fx_service.get_tt_buy_rate(lot.currency if hasattr(lot, 'currency') else 'USD', lot.date)
        cost_inr = shares_matched * lot.price * cost_fx_rate

        # Sale INR is calculated based on the FX rate at the time of sale
        sale_fx_rate = fx_service.get_tt_buy_rate(sell_currency, sell_date)
        sale_inr = shares_matched * sell_price * sale_fx_rate

        gain_inr = sale_inr - cost_inr

        results.append({
            "lot_id": lot.id,
            "shares_matched": shares_matched,
            "cost_inr": cost_inr,
            "sale_inr": sale_inr,
            "gain_inr": gain_inr,
            "holding_type": holding_type
        })

        # Update remaining shares
        shares_remaining -= shares_matched

        # Update lot available shares
        lot.available_shares -= shares_matched
        db.add(lot)

    db.commit()
    return results
>>>>>>> origin/main
