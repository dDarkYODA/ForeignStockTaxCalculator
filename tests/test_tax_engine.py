from datetime import date
from backend.models.transaction import Transaction
from backend.services.tax_engine import calculate_gains

def test_short_term_capital_gain():
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="AAPL",
            shares=10,
            price=150.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1), # Less than 24 months -> STCG
            transaction_type="SELL",
            symbol="AAPL",
            shares=5,
            price=180.0,
            currency="USD",
            broker="Test"
        )
    ]
    
    results = calculate_gains(transactions)
    assert len(results) == 1
    
    res = results[0]
    assert res.holding_type == 'STCG'
    assert res.shares == 5
    # Depending on fx mock, cost_inr and sale_inr will be evaluated.
    assert res.sale_inr > res.cost_inr

def test_long_term_capital_gain():
    transactions = [
        Transaction(
            date=date(2021, 1, 1),
            transaction_type="RSU_VEST",
            symbol="MSFT",
            shares=20,
            price=200.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2024, 1, 1), # More than 24 months -> LTCG
            transaction_type="SELL",
            symbol="MSFT",
            shares=20,
            price=300.0,
            currency="USD",
            broker="Test"
        )
    ]
    
    results = calculate_gains(transactions)
    assert len(results) == 1
    
    res = results[0]
    assert res.holding_type == 'LTCG'
