from backend.models.schema import Lot
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
    available_lots = Lot.get_available_lots(db, user_id, symbol)

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
        # Cost INR is prorated based on the lot's total cost_inr
        cost_inr = (lot.cost_inr / lot.shares) * shares_matched if lot.shares > 0 else 0

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
