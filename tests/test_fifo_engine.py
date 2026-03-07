from datetime import date
from backend.models.transaction import Transaction
from backend.services.fifo_engine import match_lots

def test_fifo_matching():
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="GOOGL",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 2, 1),
            transaction_type="BUY",
            symbol="GOOGL",
            shares=5,
            price=110.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="SELL",
            symbol="GOOGL",
            shares=12,
            price=120.0,
            currency="USD",
            broker="Test"
        )
    ]
    
    matches = match_lots(transactions)
    
    # We expect 2 matches:
    # 1. 10 shares from the first lot
    # 2. 2 shares from the second lot
    assert len(matches) == 2
    
    match1 = matches[0]
    assert match1[0].date == date(2023, 1, 1) # buy lot
    assert match1[2] == 10 # matched shares
    
    match2 = matches[1]
    assert match2[0].date == date(2023, 2, 1) # buy lot
    assert match2[2] == 2 # matched shares
