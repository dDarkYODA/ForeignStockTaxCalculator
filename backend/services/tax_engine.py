from sqlalchemy.orm import Session
from backend.models.schema import Transaction, Lot, TaxCalculation, TransactionType
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
                available_shares=txn.shares,
                currency=txn.currency
            )
            db.add(lot)

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

    # Commit the entire batch
    db.commit()
