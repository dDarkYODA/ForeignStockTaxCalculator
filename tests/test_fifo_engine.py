import pytest
from backend.services.fifo_engine import match_sell_fifo
from backend.models.schema import Lot, TransactionType, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

# Setup in-memory DB for tests
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_fifo_matching(db):
    # Buy 10 shares
    lot1 = Lot(user_id="test", symbol="AAPL", shares=10, available_shares=10, price=150.0, date=date(2023, 1, 1), cost_inr=1500.0)
    db.add(lot1)
    db.commit()

    results = match_sell_fifo(db, "test", "AAPL", 5, date(2023, 2, 1), 160.0, "USD")

    assert len(results) == 1
    assert results[0]["shares_matched"] == 5

    # Check lot is updated
    db.refresh(lot1)
    assert lot1.available_shares == 5

def test_fifo_empty_transactions(db):
    results = match_sell_fifo(db, "test", "AAPL", 5, date(2023, 2, 1), 160.0, "USD")
    assert len(results) == 0

def test_fifo_only_sells(db):
    results = match_sell_fifo(db, "test", "AAPL", 10, date(2023, 2, 1), 160.0, "USD")
    assert len(results) == 0

def test_fifo_exact_match(db):
    lot1 = Lot(user_id="test", symbol="TSLA", shares=10, available_shares=10, price=200.0, date=date(2023, 1, 1), cost_inr=2000.0)
    db.add(lot1)
    db.commit()

    results = match_sell_fifo(db, "test", "TSLA", 10, date(2023, 2, 1), 250.0, "USD")
    assert len(results) == 1
    assert results[0]["shares_matched"] == 10

    db.refresh(lot1)
    assert lot1.available_shares == 0

def test_fifo_multiple_buys_single_sell(db):
    lot1 = Lot(user_id="test", symbol="AMZN", shares=10, available_shares=10, price=100.0, date=date(2023, 1, 1), cost_inr=1000.0)
    lot2 = Lot(user_id="test", symbol="AMZN", shares=15, available_shares=15, price=110.0, date=date(2023, 2, 1), cost_inr=1650.0)
    lot3 = Lot(user_id="test", symbol="AMZN", shares=20, available_shares=20, price=120.0, date=date(2023, 3, 1), cost_inr=2400.0)
    db.add_all([lot1, lot2, lot3])
    db.commit()

    results = match_sell_fifo(db, "test", "AMZN", 30, date(2023, 4, 1), 130.0, "USD")

    assert len(results) == 3
    assert results[0]["shares_matched"] == 10
    assert results[1]["shares_matched"] == 15
    assert results[2]["shares_matched"] == 5

def test_fifo_partial_lot_consumption(db):
    lot1 = Lot(user_id="test", symbol="GOOG", shares=50, available_shares=50, price=100.0, date=date(2023, 1, 1), cost_inr=5000.0)
    db.add(lot1)
    db.commit()

    res1 = match_sell_fifo(db, "test", "GOOG", 20, date(2023, 2, 1), 110.0, "USD")
    res2 = match_sell_fifo(db, "test", "GOOG", 15, date(2023, 3, 1), 120.0, "USD")

    assert len(res1) == 1
    assert res1[0]["shares_matched"] == 20
    assert len(res2) == 1
    assert res2[0]["shares_matched"] == 15

    db.refresh(lot1)
    assert lot1.available_shares == 15
