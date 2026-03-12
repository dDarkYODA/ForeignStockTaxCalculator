import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database import Base

@pytest.fixture
def db():
    # Setup in-memory sqlite for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import date
from backend.models.schema import Lot
from backend.services.trade_simulator import simulate_trade

def test_trade_simulator_case_insensitive_symbol(db):
    # Add a lot with specific casing
    lot = Lot(
        user_id="test_user",
        symbol="Novartis Share",
        shares=100.0,
        available_shares=100.0,
        price=100.0,
        cost_inr=10000.0,
        date=date(2022, 1, 1),
        currency="USD"
    )
    db.add(lot)
    db.commit()

    # Query with different casing
    result = simulate_trade(
        db=db,
        user_id="test_user",
        symbol="NOVARTIS SHARE",
        shares=10.0,
        price=150.0,
        currency="USD",
        sale_date=date(2026, 3, 12)
    )

    assert result["capital_gain"] is not None
    assert result["breakdown"][0]["shares_matched"] == 10.0
