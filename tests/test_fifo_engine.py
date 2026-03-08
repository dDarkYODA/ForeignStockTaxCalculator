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


def test_fifo_empty_transactions():
    """Test FIFO with empty transaction list"""
    matches = match_lots([])
    assert len(matches) == 0


def test_fifo_only_buys():
    """Test FIFO with only buy transactions"""
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
            shares=20,
            price=160.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 0


def test_fifo_only_sells():
    """Test FIFO with only sell transactions (no inventory to match)"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="SELL",
            symbol="MSFT",
            shares=10,
            price=280.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 0


def test_fifo_exact_match():
    """Test FIFO when sell exactly matches buy quantity"""
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
            date=date(2023, 2, 1),
            transaction_type="SELL",
            symbol="TSLA",
            shares=10,
            price=250.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1
    assert matches[0][2] == 10  # All shares matched


def test_fifo_multiple_sells():
    """Test FIFO with multiple sell transactions"""
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
            date=date(2023, 2, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=30,
            price=320.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=40,
            price=340.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 4, 1),
            transaction_type="SELL",
            symbol="NFLX",
            shares=30,
            price=360.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 3
    assert sum(m[2] for m in matches) == 100  # Total matched shares


def test_fifo_multiple_buys_single_sell():
    """Test FIFO with multiple buy lots and single sell consuming multiple lots"""
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
            shares=15,
            price=110.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="BUY",
            symbol="AMZN",
            shares=20,
            price=120.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 4, 1),
            transaction_type="SELL",
            symbol="AMZN",
            shares=30,
            price=130.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    # Should consume first lot (10) + second lot (15) + part of third (5)
    assert len(matches) == 3
    assert matches[0][2] == 10  # First lot fully consumed
    assert matches[1][2] == 15  # Second lot fully consumed
    assert matches[2][2] == 5   # Third lot partially consumed


def test_fifo_unsorted_transactions():
    """Test FIFO with transactions not in date order"""
    transactions = [
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="SELL",
            symbol="META",
            shares=10,
            price=320.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="META",
            shares=15,
            price=300.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 2, 1),
            transaction_type="BUY",
            symbol="META",
            shares=5,
            price=310.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    # Should sort by date and match correctly
    assert len(matches) == 1
    assert matches[0][0].date == date(2023, 1, 1)  # First buy lot matched
    assert matches[0][2] == 10


def test_fifo_rsu_vest_transaction():
    """Test FIFO with RSU_VEST transaction type (treated as buy)"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="RSU_VEST",
            symbol="GOOGL",
            shares=20,
            price=95.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="GOOGL",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1
    assert matches[0][0].transaction_type == "RSU_VEST"
    assert matches[0][2] == 10


def test_fifo_case_insensitive_sell():
    """Test FIFO recognizes 'sell' in lowercase or mixed case"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="NVDA",
            shares=10,
            price=450.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 2, 1),
            transaction_type="sell",  # lowercase
            symbol="NVDA",
            shares=5,
            price=480.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1
    assert matches[0][2] == 5


def test_fifo_sell_all_transaction():
    """Test FIFO with 'Sell All' transaction type"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="AMD",
            shares=25,
            price=80.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="Sell All",  # Contains 'sell'
            symbol="AMD",
            shares=25,
            price=100.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1
    assert matches[0][2] == 25


def test_fifo_fractional_shares():
    """Test FIFO with fractional shares"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="INTC",
            shares=10.5,
            price=45.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 6, 1),
            transaction_type="SELL",
            symbol="INTC",
            shares=5.25,
            price=50.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1
    assert matches[0][2] == 5.25


def test_fifo_partial_lot_consumption():
    """Test FIFO leaves partial inventory after sell"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="GOOG",
            shares=50,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 2, 1),
            transaction_type="SELL",
            symbol="GOOG",
            shares=20,
            price=110.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 3, 1),
            transaction_type="SELL",
            symbol="GOOG",
            shares=15,
            price=120.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 2
    # Both sells should match against the same buy lot
    assert matches[0][0].date == date(2023, 1, 1)
    assert matches[1][0].date == date(2023, 1, 1)
    assert matches[0][2] == 20
    assert matches[1][2] == 15



def test_fifo_match_structure():
    """Test that match tuples have correct structure"""
    transactions = [
        Transaction(
            date=date(2023, 1, 1),
            transaction_type="BUY",
            symbol="TEST",
            shares=10,
            price=100.0,
            currency="USD",
            broker="Test"
        ),
        Transaction(
            date=date(2023, 2, 1),
            transaction_type="SELL",
            symbol="TEST",
            shares=5,
            price=110.0,
            currency="USD",
            broker="Test"
        )
    ]

    matches = match_lots(transactions)
    assert len(matches) == 1

    match = matches[0]
    # Match should be tuple of (buy_tx, sell_tx, shares)
    assert len(match) == 3
    assert isinstance(match[0], Transaction)  # Buy transaction
    assert isinstance(match[1], Transaction)  # Sell transaction
    assert isinstance(match[2], (int, float))  # Matched shares
    assert match[0].transaction_type == "BUY"
    assert match[1].transaction_type == "SELL"