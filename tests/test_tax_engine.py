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


def test_calculate_gains_empty_list():
    """Test calculate_gains with empty transaction list"""
    results = calculate_gains([])
    assert len(results) == 0


def test_calculate_gains_only_buys():
    """Test calculate_gains with only buy transactions"""
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
            date=date(2023, 2, 1),
            transaction_type="BUY",
            symbol="AAPL",
            shares=5,
            price=160.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 0  # No sells, no gains to calculate


def test_calculate_gains_multiple_currencies():
    """Test calculate_gains with different currencies"""
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
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="AAPL",
            shares=5,
            price=180.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="TCS",
            shares=10,
            price=3000.0,
            currency="INR",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="TCS",
            shares=5,
            price=3500.0,
            currency="INR",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 2


def test_calculate_gains_with_loss():
    """Test calculate_gains when sale price is lower than cost"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="NFLX",
            shares=10,
            price=400.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=10,
            price=300.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].gain_inr < 0  # Loss


def test_calculate_gains_boundary_25_months():
    """Test exactly 25 months (should be LTCG)"""
    transactions = [
        Transaction(
            date=date(2020, 1, 1),
            transaction_type="BUY",
            symbol="GOOGL",
            shares=10,
            price=1500.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2022, 2, 1),  # 25 months later
            transaction_type="SELL",
            symbol="GOOGL",
            shares=10,
            price=2000.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].holding_type == 'LTCG'


def test_calculate_gains_same_day():
    """Test buy and sell on same day (0 months - STCG)"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="TSLA",
            shares=10,
            price=200.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="SELL",
            symbol="TSLA",
            shares=10,
            price=220.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].holding_type == 'STCG'


def test_calculate_gains_fractional_shares():
    """Test calculate_gains with fractional shares"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="BRK.B",
            shares=10.5,
            price=300.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="BRK.B",
            shares=3.25,
            price=320.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].shares == 3.25


def test_calculate_gains_zero_shares():
    """Test calculate_gains with zero shares"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="META",
            shares=0,
            price=300.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="META",
            shares=0,
            price=320.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    # FIFO engine filters out zero share transactions
    # This is expected behavior - no meaningful gain to calculate
    assert len(results) == 0


def test_calculate_gains_fifo_complex():
    """Test complex FIFO scenario with multiple buys and sells"""
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
            date=date(2023, 2, 1),
            transaction_type="BUY",
            symbol="AMZN",
            shares=20,
            price=110.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="BUY",
            symbol="AMZN",
            shares=15,
            price=105.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="AMZN",
            shares=35,
            price=120.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    # Should match: 10 + 20 + 5 = 35 shares from three lots
    assert len(results) == 3
    total_shares = sum(r.shares for r in results)
    assert total_shares == 35


def test_calculate_gains_different_symbols_no_mixing():
    """Test that different symbols don't mix in FIFO"""
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
            shares=10,
            price=2000.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="GOOGL",
            shares=5,
            price=2200.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1
    # Should only match GOOGL, not AAPL
    assert results[0].symbol == "GOOGL"


def test_calculate_gains_inr_conversion():
    """Test INR conversion is applied correctly"""
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
            date=date(2023, 2, 1),
            transaction_type="SELL",
            symbol="AAPL",
            shares=10,
            price=160.0,
            currency="USD",
            broker="Test"
        )
    ]

    results = calculate_gains(transactions)
    assert len(results) == 1

    # Check that INR values are greater than USD values (converted)
    assert results[0].cost_inr > 150.0 * 10  # Should be multiplied by FX rate
    assert results[0].sale_inr > 160.0 * 10


def test_calculate_gains_date_sorting():
    """Test that transactions are processed in date order"""
    transactions = [
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="IBM",
            shares=5,
            price=130.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="IBM",
            shares=10,
            price=120.0,
            currency="USD",
            broker="Test"
        )
    ]

    # Transactions are out of order, should still work
    results = calculate_gains(transactions)
    assert len(results) == 1
    assert results[0].shares == 5