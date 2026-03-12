with open('tests/test_trade_simulator.py', 'r') as f:
    content = f.read()

content = """import pytest
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

""" + content

with open('tests/test_trade_simulator.py', 'w') as f:
    f.write(content)
