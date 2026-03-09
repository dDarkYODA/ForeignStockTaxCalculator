from sqlalchemy.orm import Session
from datetime import date
from backend.models.schema import Lot
from .fx_service import fx_service

def simulate_trade(db: Session, user_id: str, symbol: str, shares: float, price: float, currency: str, sale_date: date):
    """
    Simulates a trade without altering the database.
    Calculates cost basis using FIFO, and estimates capital gains tax.
    """
    # Fetch available lots, order by date (FIFO)
    available_lots = db.query(Lot).filter(
        Lot.user_id == user_id,
        Lot.symbol == symbol,
        Lot.available_shares > 0
    ).order_by(Lot.date).all()

    shares_remaining = shares
    cost_basis_inr = 0.0
    lots_matched = []

    sale_fx_rate = fx_service.get_tt_buy_rate(currency, sale_date)
    sale_inr_total = 0.0
    stcg_gain_inr = 0.0
    ltcg_gain_inr = 0.0

    for lot in available_lots:
        if shares_remaining <= 0:
            break

        shares_matched = min(shares_remaining, lot.available_shares)

        # Calculate cost in INR for the matched shares prorated from lot total cost_inr
        lot_cost_inr = (lot.cost_inr / lot.shares) * shares_matched if lot.shares > 0 else 0

        # Calculate sale value in INR for these shares
        lot_sale_inr = shares_matched * price * sale_fx_rate
        lot_gain_inr = lot_sale_inr - lot_cost_inr

        # Determine holding type (24 months)
        months_held = (sale_date.year - lot.date.year) * 12 + sale_date.month - lot.date.month
        if sale_date.day < lot.date.day:
            months_held -= 1

        holding_type = "LTCG" if months_held >= 24 else "STCG"

        if holding_type == "LTCG":
            ltcg_gain_inr += lot_gain_inr
        else:
            stcg_gain_inr += lot_gain_inr

        lots_matched.append({
            "date": lot.date,
            "shares_matched": shares_matched,
            "cost_inr": lot_cost_inr,
            "sale_inr": lot_sale_inr,
            "gain_inr": lot_gain_inr,
            "holding_type": holding_type
        })

        cost_basis_inr += lot_cost_inr
        sale_inr_total += lot_sale_inr
        shares_remaining -= shares_matched

    if shares_remaining > 0:
        # User is trying to sell more than they own
        raise ValueError(f"Insufficient shares. You only have {shares - shares_remaining} shares available for {symbol}.")

    capital_gain_inr = sale_inr_total - cost_basis_inr

    # Tax Calculation
    # STCG -> 30%
    # LTCG -> 12.5%
    tax_stcg = stcg_gain_inr * 0.30 if stcg_gain_inr > 0 else 0.0
    tax_ltcg = ltcg_gain_inr * 0.125 if ltcg_gain_inr > 0 else 0.0

    total_tax_estimated = tax_stcg + tax_ltcg
    net_after_tax = sale_inr_total - total_tax_estimated

    return {
        "sale_value": sale_inr_total,
        "cost_basis": cost_basis_inr,
        "capital_gain": capital_gain_inr,
        "tax": total_tax_estimated,
        "net_after_tax": net_after_tax,
        "breakdown": lots_matched
    }
