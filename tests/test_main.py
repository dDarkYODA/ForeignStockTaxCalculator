
from fastapi.testclient import TestClient
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
from sqlalchemy.pool import StaticPool
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def setup_db_with_transactions(transactions, db):
    db.query(TaxCalculation).delete()
    db.query(Lot).delete()
    db.query(DBTransaction).delete()
    db.commit()
    for tx in transactions:
        db_tx = DBTransaction(**tx, user_id="mock_user")
        db.add(db_tx)
    db.commit()
    process_transactions(db, "mock_user")

def test_read_root(client):
    """Test root endpoint returns OK status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the Foreign Stock Tax Calculator API"

def test_upload_shareworks_valid(client):
    """Test uploading a valid Shareworks CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-01-15', 'RSU', 'GOOGL', '10', '95.50'])
        writer.writerow(['2023-06-20', 'SELL', 'GOOGL', '5', '120.00'])
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=shareworks",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'success'
        transactions = client.get('/api/transactions').json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'GOOGL'
        assert transactions[0]['broker'] == 'Shareworks'
    finally:
        os.unlink(temp_file)

def test_upload_fidelity_valid(client):
    """Test uploading a valid Fidelity CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-02-10', 'Buy', 'AAPL', '20', '150.00'])
        writer.writerow(['2024-03-15', 'Sell', 'AAPL', '10', '180.00'])
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=fidelity",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'success'
        transactions = client.get('/api/transactions').json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'AAPL'
        assert transactions[0]['broker'] == 'Fidelity'
    finally:
        os.unlink(temp_file)

def test_upload_generic_parser(client):
    """Test uploading a file with unknown broker (triggers generic AI parser)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Trade Date', 'Plan Type', 'Ticker', 'Shares', 'Price', 'Currency'])
        writer.writerow(['2023-03-01', 'Buy', 'MSFT', '15', '280.00', 'USD'])
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=generic",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] in ('success', 'requires_mapping')
    finally:
        os.unlink(temp_file)

def test_upload_invalid_file(client):
    """Test uploading an invalid CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("This is not a valid CSV file\nwith proper structure")
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=shareworks",
                files={"file": ("test.csv", f, "text/csv")}
            )

        # Should return error for invalid file
        assert response.status_code == 400
    finally:
        os.unlink(temp_file)

def test_upload_missing_file(client):
    """Test upload endpoint without providing a file"""
    response = client.post("/api/upload?broker=shareworks")
    assert response.status_code == 422  # Validation error

def test_calculate_tax_valid(client, db_session):
    """Test calculate endpoint with valid transactions"""
    transactions = [
        {
            "date": date(2023, 1, 1),
            "transaction_type": "BUY",
            "symbol": "GOOGL",
            "shares": 10.0,
            "price": 100.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": date(2023, 6, 1),
            "transaction_type": "SELL",
            "symbol": "GOOGL",
            "shares": 5.0,
            "price": 120.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    setup_db_with_transactions(transactions, db_session)
    response = client.get("/api/capital-gains")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]['holding_type'] == 'STCG'
    assert results[0]['shares'] == 5.0

def test_calculate_tax_empty_list(client, db_session):
    """Test calculate endpoint with empty transaction list"""
    setup_db_with_transactions([], db_session)
    response = client.get("/api/capital-gains")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0

def test_calculate_tax_no_sales(client, db_session):
    """Test calculate endpoint with only buy transactions"""
    transactions = [
        {
            "date": date(2023, 1, 1),
            "transaction_type": "BUY",
            "symbol": "AAPL",
            "shares": 10.0,
            "price": 150.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    setup_db_with_transactions(transactions, db_session)
    response = client.get("/api/capital-gains")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0  # No sales means no tax results

def test_cors_configuration(client):
    """Test that CORS is configured correctly"""
    # Test with a specific origin
    # Since app is initialized once, we check its middleware state
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = next((m for m in app.user_middleware if m.cls == CORSMiddleware), None)
    assert cors_middleware is not None, "CORS middleware should be configured"

    # Verify behavior via headers
    # If ALLOWED_ORIGINS is empty (default), no Access-Control-Allow-Origin should be present
    response = client.get("/", headers={"Origin": "http://malicious.com"})
    assert "access-control-allow-origin" not in response.headers

def test_upload_empty_csv(client):
    """Test uploading an empty CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=shareworks",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'success'
        transactions = client.get('/api/transactions').json()
        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)

def test_calculate_long_term_gains(client, db_session):
    """Test calculate endpoint with long-term capital gains (>24 months)"""
    transactions = [
        {
            "date": date(2020, 1, 1),
            "transaction_type": "BUY",
            "symbol": "TSLA",
            "shares": 100.0,
            "price": 50.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": date(2024, 2, 1),
            "transaction_type": "SELL",
            "symbol": "TSLA",
            "shares": 50.0,
            "price": 200.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    setup_db_with_transactions(transactions, db_session)
    response = client.get("/api/capital-gains")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]['holding_type'] == 'LTCG'
    assert results[0]['gain_inr'] > 0
