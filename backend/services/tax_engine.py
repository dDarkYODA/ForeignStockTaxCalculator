<<<<<<< HEAD
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
=======
from sqlalchemy.orm import Session
from models.schema import Transaction, Lot, TaxCalculation, TransactionType
from .fifo_engine import match_sell_fifo
from .fx_service import fx_service

def process_transactions(db: Session, user_id: str):
    """
    Processes all transactions for a user, creates lots for buys/vests,
    and calculates capital gains for sells.
    """

    # 1. Clear existing lots and tax calculations for this user to ensure idempotency
    db.query(Lot).filter(Lot.user_id == user_id).delete()
    db.query(TaxCalculation).filter(TaxCalculation.user_id == user_id).delete()
    db.commit()

    # 2. Get all transactions ordered by date
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.date).all()

    for txn in transactions:
        if txn.transaction_type in [TransactionType.BUY, TransactionType.RSU_VEST, TransactionType.ESPP_PURCHASE]:
            # Create a new lot
            fx_rate = fx_service.get_tt_buy_rate(txn.currency, txn.date)
            cost_inr = txn.shares * txn.price * fx_rate

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
            db.add(lot)
            db.commit()

        elif txn.transaction_type == TransactionType.SELL:
            # Match against lots and calculate tax
            match_results = match_sell_fifo(
                db=db,
                user_id=user_id,
                symbol=txn.symbol,
                shares_to_sell=txn.shares,
                sell_date=txn.date,
                sell_price=txn.price,
                sell_currency=txn.currency
            )

            # Save tax calculations
            for result in match_results:
                tax_calc = TaxCalculation(
                    user_id=user_id,
                    sell_transaction_id=txn.id,
                    date=txn.date,
                    symbol=txn.symbol,
                    shares=result["shares_matched"],
                    cost_inr=result["cost_inr"],
                    sale_inr=result["sale_inr"],
                    gain_inr=result["gain_inr"],
                    holding_type=result["holding_type"]
                )
                db.add(tax_calc)

            db.commit()
>>>>>>> origin/main
