from sqlalchemy.orm import Session
from datetime import date
from collections import defaultdict
from backend.models.schema import Lot
from .fx_service import fx_service
from .price_service import price_service

def get_portfolio(db: Session, user_id: str, manual_prices: dict = None):
    """
    Computes portfolio holdings and summary statistics based on available lots.
    """
    if manual_prices is None:
        manual_prices = {}

    lots = db.query(Lot).filter(Lot.user_id == user_id, Lot.available_shares > 0).all()

    holdings_dict = defaultdict(lambda: {
        "symbol": "",
        "shares": 0.0,
        "total_cost_local": 0.0,
        "cost_inr": 0.0
    })

    for lot in lots:
        h = holdings_dict[lot.symbol]
        h["symbol"] = lot.symbol
        h["shares"] += lot.available_shares

        # Calculate local cost for available shares only
        cost_local_lot = lot.available_shares * lot.price
        h["total_cost_local"] += cost_local_lot

        # Calculate INR cost for available shares
        # Note: lot.cost_inr stores total initial cost. We need proportional cost_inr.
        # Alternatively, recalculate using fx_rate at lot.date.
        # Assuming lot has currency property from earlier assumption.
        # But let's safely use the proportional cost_inr just in case.
        if lot.shares > 0:
            proportional_cost_inr = (lot.cost_inr / lot.shares) * lot.available_shares
            h["cost_inr"] += proportional_cost_inr

    today = date.today()
    holdings_list = []
    total_cost_inr = 0.0
    total_value_inr = 0.0

    for symbol, h in holdings_dict.items():
        shares = h["shares"]
        avg_cost_local = h["total_cost_local"] / shares if shares > 0 else 0.0
        cost_inr = h["cost_inr"]

        manual_price = manual_prices.get(symbol)
        current_price = price_service.get_current_price(symbol, manual_price)

        currency = "USD" # Default in case no lots are found, but we shouldn't hit this
        sample_lot = next((l for l in lots if l.symbol == symbol), None)
        if sample_lot and sample_lot.currency:
            currency = sample_lot.currency

        # Value INR = shares * current_price * fx(today)
        fx_rate = fx_service.get_tt_buy_rate(currency, today)
        value_inr = shares * current_price * fx_rate

        unrealized_gain = value_inr - cost_inr
        gain_percent = (unrealized_gain / cost_inr) * 100 if cost_inr > 0 else 0.0

        holdings_list.append({
            "symbol": symbol,
            "shares": shares,
            "avg_cost_local": avg_cost_local,
            "cost_inr": cost_inr,
            "current_price": current_price,
            "value_inr": value_inr,
            "unrealized_gain": unrealized_gain,
            "gain_percent": gain_percent
        })

        total_cost_inr += cost_inr
        total_value_inr += value_inr

    total_unrealized_gain = total_value_inr - total_cost_inr

    # Sort holdings by value descending
    holdings_list.sort(key=lambda x: x["value_inr"], reverse=True)

    return {
        "summary": {
            "total_cost_inr": total_cost_inr,
            "total_value_inr": total_value_inr,
            "total_unrealized_gain": total_unrealized_gain
        },
        "holdings": holdings_list
    }
