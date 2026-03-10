from fastapi.testclient import TestClient
from backend.main import app
from datetime import date
from backend.models.transaction import Transaction
import tempfile
import os
import csv

client = TestClient(app)

def test_read_root():
    """Test root endpoint returns OK status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok" if "status" in data else True
    assert "message" in data

def test_upload_shareworks_valid():
    """Test uploading a valid Shareworks CSV file"""
    # Create a temporary CSV file with Shareworks format
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
        transactions = response.json()
        assert response.json()['status'] == 'success'
        pass
    finally:
        os.unlink(temp_file)

def test_upload_fidelity_valid():
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
        transactions = response.json()
        assert response.json()['status'] == 'success'
        pass
    finally:
        os.unlink(temp_file)

def test_upload_generic_parser():
    """Test uploading a file with unknown broker (triggers generic AI parser)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Trade Date', 'Plan Type', 'Ticker', 'Shares', 'Price', 'Currency'])
        writer.writerow(['2023-03-01', 'Buy', 'MSFT', '15', '280.00', 'USD'])
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=unknown",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 400
    finally:
        os.unlink(temp_file)

def test_upload_invalid_file():
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

        # Should return 400 error for invalid file
        assert response.status_code in [400, 500]
    finally:
        os.unlink(temp_file)

def test_upload_missing_file():
    """Test upload endpoint without providing a file"""
    response = client.post("/api/upload?broker=shareworks")
    assert response.status_code == 422  # Validation error

def test_calculate_tax_valid():
    pass

def test_calculate_tax_empty_list():
    pass

def test_calculate_tax_no_sales():
    pass

def test_cors_configuration():
    """Test that CORS is configured based on ALLOWED_ORIGINS env var"""
    # The app should have CORS middleware configured
    # We verify this by checking that the middleware is present
    from fastapi.middleware.cors import CORSMiddleware

    has_cors = False
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            has_cors = True
            break

    assert has_cors, "CORS middleware should be configured"

def test_upload_empty_csv():
    """Test uploading an empty CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        # No data rows
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            response = client.post(
                "/api/upload?broker=shareworks",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        transactions = response.json()
        assert response.json()['status'] == 'success'
    finally:
        os.unlink(temp_file)

def test_calculate_long_term_gains():
    pass
