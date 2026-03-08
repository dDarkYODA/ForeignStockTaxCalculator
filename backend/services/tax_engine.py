from datetime import date
from dateutil.relativedelta import relativedelta
from backend.models.transaction import Transaction, TaxResult
from backend.services.fx_service import get_tt_buy_rate
from backend.services.fifo_engine import match_lots

def calculate_gains(transactions: list[Transaction]) -> list[TaxResult]:
    matches = match_lots(transactions)
    results = []
    
    # Check if there are matches at all. If no sales were found, matching returns empty list.
    if not matches:
        return []

    for buy_tx, sell_tx, shares in matches:
        cost_rate = get_tt_buy_rate(buy_tx.currency, buy_tx.date)
        sell_rate = get_tt_buy_rate(sell_tx.currency, sell_tx.date)

        cost_inr = shares * buy_tx.price * cost_rate
        sale_inr = shares * sell_tx.price * sell_rate
        gain_inr = sale_inr - cost_inr

        # Calculate holding period
        months_held = (sell_tx.date.year - buy_tx.date.year) * 12 + sell_tx.date.month - buy_tx.date.month

        # In python dateutil we can use relativedelta to precisely check
        holding_diff = relativedelta(sell_tx.date, buy_tx.date)
        total_months = holding_diff.years * 12 + holding_diff.months

        # Rule: > 24 months for foreign unlisted/listed shares is LTCG
        holding_type = 'LTCG' if total_months > 24 else 'STCG'

        res = TaxResult(
            date=sell_tx.date,
            symbol=sell_tx.symbol,
            shares=shares,
            cost_inr=cost_inr,
            sale_inr=sale_inr,
            gain_inr=gain_inr,
            holding_type=holding_type
        )
        results.append(res)

    return results
