from datetime import date
from backend.models.transaction import Transaction
from backend.services.tax_engine import process_transactions
def calculate_gains(transactions):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.database import Base
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    for t in transactions:
        from backend.models.schema import Transaction as DBTransaction
        db.add(DBTransaction(**t.dict(), user_id="test"))
    db.commit()
    process_transactions(db, "test")
    from backend.models.schema import TaxCalculation
    return db.query(TaxCalculation).all()

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


def test_exactly_24_months_is_stcg():
    """Test that exactly 24 months holding period is STCG (needs >24 for LTCG)"""
    transactions = [
        Transaction(
            date=date(2022, 1, 1),
            transaction_type="BUY",
            symbol="GOOGL",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2024, 1, 1),  # Exactly 24 months
            transaction_type="SELL",
            symbol="GOOGL",
            shares=10,
            price=150.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].holding_type == 'STCG'


def test_25_months_is_ltcg():
    """Test that 25 months holding period is LTCG"""
    transactions = [
        Transaction(
            date=date(2022, 1, 1),
            transaction_type="BUY",
            symbol="TSLA",
            shares=15,
            price=200.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2024, 2, 1),  # 25 months
            transaction_type="SELL",
            symbol="TSLA",
            shares=15,
            price=250.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].holding_type == 'LTCG'


def test_multiple_sales_from_same_lot():
    """Test multiple sales from the same buy lot"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="NFLX",
            shares=100,
            price=300.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=30,
            price=350.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 12, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=40,
            price=400.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 2
    assert results[0].shares == 30
    assert results[1].shares == 40
    assert all(r.holding_type == 'STCG' for r in results)


def test_empty_transactions_list():
    """Test calculate_gains with empty transaction list"""
    results = calculate_gains([])
    assert len(results) == 0


def test_only_buy_transactions():
    """Test with only buy transactions (no sales)"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="AMZN",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="BUY",
            symbol="AMZN",
            shares=20,
            price=110.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 0


def test_gain_calculation_accuracy():
    """Test that gain calculations are accurate in INR"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="META",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="META",
            shares=10,
            price=150.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1

    res = results[0]
    assert res.cost_inr > 0
    assert res.sale_inr > 0
    assert res.gain_inr == res.sale_inr - res.cost_inr


def test_loss_transaction():
    """Test calculation when sale price is lower than purchase price"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="NVDA",
            shares=10,
            price=500.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="NVDA",
            shares=10,
            price=400.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].gain_inr < 0  # Loss


def test_different_currencies():
    """Test transactions with different currencies"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="VOD",
            shares=100,
            price=10.0,
            currency="GBP",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="VOD",
            shares=100,
            price=12.0,
            currency="GBP",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    # Should still calculate (with default FX rate for GBP)
    assert results[0].cost_inr > 0
    assert results[0].sale_inr > 0


def test_fractional_shares():
    """Test with fractional shares"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="GOOG",
            shares=10.5,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="GOOG",
            shares=5.25,
            price=120.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].shares == 5.25


def test_multiple_symbols():
    """Test with multiple different symbols"""
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
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="GOOGL",
            shares=5,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="AAPL",
            shares=5,
            price=180.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2025, 6, 1),
            transaction_type="SELL",
            symbol="GOOGL",
            shares=5,
            price=150.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 2
    assert results[0].symbol == "AAPL"
    assert results[0].holding_type == 'STCG'
    assert results[1].symbol == "GOOGL"
    assert results[1].holding_type == 'LTCG'


def test_result_contains_all_fields():
    """Test that result objects contain all required fields"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="AMD",
            shares=10,
            price=80.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="AMD",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1

    res = results[0]
    assert hasattr(res, 'date')
    assert hasattr(res, 'symbol')
    assert hasattr(res, 'shares')
    assert hasattr(res, 'cost_inr')
    assert hasattr(res, 'sale_inr')
    assert hasattr(res, 'gain_inr')
    assert hasattr(res, 'holding_type')