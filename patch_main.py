import re

with open("tests/test_main.py", "r") as f:
    content = f.read()

# 1. Remove duplicate setup_db_with_transactions
content = re.sub(
    r'def setup_db_with_transactions\(transactions\):\n    with next\(get_db\(\)\) as db:\n        db\.query\(TaxCalculation\)\.delete\(\)\n        db\.query\(Lot\)\.delete\(\)\n        db\.query\(DBTransaction\)\.delete\(\)\n        db\.commit\(\)\n        for tx in transactions:\n            db_tx = DBTransaction\(\*\*tx, user_id="mock_user"\)\n            db\.add\(db_tx\)\n        db\.commit\(\)\n        process_transactions\(db, "mock_user"\)\n\n\ndef setup_db_with_transactions\(transactions\):\n    with next\(get_db\(\)\) as db:\n        db\.query\(TaxCalculation\)\.delete\(\)\n        db\.query\(Lot\)\.delete\(\)\n        db\.query\(DBTransaction\)\.delete\(\)\n        db\.commit\(\)\n        for tx in transactions:\n            db_tx = DBTransaction\(\*\*tx, user_id="mock_user"\)\n            db\.add\(db_tx\)\n        db\.commit\(\)\n        process_transactions\(db, "mock_user"\)',
    """def setup_db_with_transactions(transactions, db):
    db.query(TaxCalculation).delete()
    db.query(Lot).delete()
    db.query(DBTransaction).delete()
    db.commit()
    for tx in transactions:
        db_tx = DBTransaction(**tx, user_id="mock_user")
        db.add(db_tx)
    db.commit()
    process_transactions(db, "mock_user")""",
    content
)

# 2. Fix test_read_root
content = content.replace('assert data["status"] == "ok" if "status" in data else True if "status" in data else True', 'assert "status" in data\n    assert data["status"] == "ok"')

# 3. Create db fixture
replacement_imports = """from fastapi.testclient import TestClient
from backend.main import app
from datetime import date
import tempfile
import os
import csv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database import get_db, Base
from backend.models.schema import Transaction as DBTransaction, Lot, TaxCalculation
from backend.services.tax_engine import process_transactions

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()"""

# Replace imports and module level setup
content = re.sub(
    r'from fastapi\.testclient import TestClient\nfrom backend\.main import app\nfrom datetime import date\nimport tempfile\nimport os\nimport csv\nfrom backend\.models\.database import get_db, Base, engine\nfrom backend\.models\.schema import Transaction as DBTransaction, Lot, TaxCalculation\nfrom backend\.services\.tax_engine import process_transactions\n\nBase\.metadata\.drop_all\(bind=engine\)\nBase\.metadata\.create_all\(bind=engine\)\n\nclient = TestClient\(app\)',
    replacement_imports,
    content
)


# Add client and db_session fixtures to tests that need them
content = re.sub(r'def test_read_root\(\):', r'def test_read_root(client):', content)
content = re.sub(r'def test_upload_shareworks_valid\(\):', r'def test_upload_shareworks_valid(client):', content)
content = re.sub(r'def test_upload_fidelity_valid\(\):', r'def test_upload_fidelity_valid(client):', content)
content = re.sub(r'def test_upload_generic_parser\(\):', r'def test_upload_generic_parser(client):', content)
content = re.sub(r'def test_upload_invalid_file\(\):', r'def test_upload_invalid_file(client):', content)
content = re.sub(r'def test_upload_missing_file\(\):', r'def test_upload_missing_file(client):', content)
content = re.sub(r'def test_calculate_tax_valid\(\):', r'def test_calculate_tax_valid(client, db_session):', content)
content = re.sub(r'setup_db_with_transactions\(transactions\)', r'setup_db_with_transactions(transactions, db_session)', content)
content = re.sub(r'def test_calculate_tax_empty_list\(\):', r'def test_calculate_tax_empty_list(client, db_session):', content)
content = re.sub(r'setup_db_with_transactions\(\[\]\)', r'setup_db_with_transactions([], db_session)', content)
content = re.sub(r'def test_calculate_tax_no_sales\(\):', r'def test_calculate_tax_no_sales(client, db_session):', content)
content = re.sub(r'def test_cors_configuration\(\):', r'def test_cors_configuration():', content) # doesn't need client
content = re.sub(r'def test_upload_empty_csv\(\):', r'def test_upload_empty_csv(client):', content)
content = re.sub(r'def test_calculate_long_term_gains\(\):', r'def test_calculate_long_term_gains(client, db_session):', content)

with open("tests/test_main.py", "w") as f:
    f.write(content)
