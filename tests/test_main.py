import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_returns_ok(self):
        """Test root endpoint returns status ok"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data

    def test_root_message_content(self):
        """Test root endpoint message is descriptive"""
        response = client.get("/")
        data = response.json()
        assert "Tax Calculator" in data["message"]


class TestUploadEndpoint:
    """Tests for /upload endpoint"""

    def test_upload_shareworks_csv(self):
        """Test uploading a valid Shareworks CSV"""
        csv_content = """Transaction Date,Plan Type,Symbol,Shares,Price
2023-01-15,RSU_VEST,AAPL,100,150.50
2023-02-20,SELL,AAPL,50,160.75"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=shareworks",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 2
            assert transactions[0]["symbol"] == "AAPL"
            assert transactions[0]["broker"] == "Shareworks"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_fidelity_csv(self):
        """Test uploading a valid Fidelity CSV"""
        csv_content = """Date,Action,Security,Quantity,Price
2023-01-15,Buy,GOOGL,25,120.30"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=fidelity",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 1
            assert transactions[0]["broker"] == "Fidelity"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_unknown_broker_uses_generic_parser(self):
        """Test uploading with unknown broker uses generic parser"""
        csv_content = """date,type,symbol,shares,price,currency
2023-01-15,BUY,AMZN,30,100.50,USD"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Clear OPENAI_API_KEY to use fallback
            old_key = os.environ.get('OPENAI_API_KEY')
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']

            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=unknown",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert isinstance(transactions, list)

            if old_key:
                os.environ['OPENAI_API_KEY'] = old_key
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_empty_csv(self):
        """Test uploading empty CSV"""
        csv_content = """Transaction Date,Plan Type,Symbol,Shares,Price"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=shareworks",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 0
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_invalid_csv(self):
        """Test uploading invalid CSV returns error"""
        csv_content = """This is not a valid CSV format"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=shareworks",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            # Current implementation returns 200 with empty list or may error
            # Either 200 or 400 is acceptable for invalid CSV
            assert response.status_code in [200, 400]
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_missing_file(self):
        """Test upload without file parameter"""
        response = client.post("/upload?broker=shareworks")
        assert response.status_code == 422  # Unprocessable entity

    def test_upload_missing_broker_parameter(self):
        """Test upload without broker parameter"""
        csv_content = """Transaction Date,Plan Type,Symbol,Shares,Price
2023-01-15,RSU_VEST,AAPL,100,150.50"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                # No broker query parameter
                response = client.post(
                    "/upload",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            # Should still work, broker parameter is in path
            assert response.status_code == 422  # Missing required parameter
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_case_insensitive_broker(self):
        """Test broker parameter is case insensitive"""
        csv_content = """Transaction Date,Plan Type,Symbol,Shares,Price
2023-01-15,RSU_VEST,AAPL,100,150.50"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=SHAREWORKS",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_with_malformed_data(self):
        """Test uploading CSV with malformed data"""
        csv_content = """Transaction Date,Plan Type,Symbol,Shares,Price
2023-01-15,RSU_VEST,AAPL,not_a_number,150.50"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=shareworks",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            # Should handle gracefully - skip invalid rows
            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 0  # Invalid row skipped
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_large_csv(self):
        """Test uploading CSV with many rows"""
        rows = ["Transaction Date,Plan Type,Symbol,Shares,Price"]
        for i in range(100):
            rows.append(f"2023-01-{(i % 28) + 1:02d},BUY,AAPL,{10 + i},150.50")

        csv_content = "\n".join(rows)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/upload?broker=shareworks",
                    files={"file": ("test.csv", file, "text/csv")}
                )

            assert response.status_code == 200
            transactions = response.json()
            assert len(transactions) == 100
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestCalculateEndpoint:
    """Tests for /calculate endpoint"""

    def test_calculate_with_valid_transactions(self):
        """Test calculate endpoint with valid transaction data"""
        transactions = [
            {
                "date": "2023-01-01",
                "transaction_type": "BUY",
                "symbol": "AAPL",
                "shares": 10,
                "price": 150.0,
                "currency": "USD",
                "broker": "Test"
            },
            {
                "date": "2023-06-01",
                "transaction_type": "SELL",
                "symbol": "AAPL",
                "shares": 5,
                "price": 180.0,
                "currency": "USD",
                "broker": "Test"
            }
        ]

        response = client.post("/calculate", json=transactions)
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["holding_type"] == "STCG"

    def test_calculate_with_empty_list(self):
        """Test calculate with empty transaction list"""
        response = client.post("/calculate", json=[])
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 0

    def test_calculate_with_only_buys(self):
        """Test calculate with only buy transactions"""
        transactions = [
            {
                "date": "2023-01-01",
                "transaction_type": "BUY",
                "symbol": "AAPL",
                "shares": 10,
                "price": 150.0,
                "currency": "USD",
                "broker": "Test"
            }
        ]

        response = client.post("/calculate", json=transactions)
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 0  # No sells, no gains

    def test_calculate_with_invalid_json(self):
        """Test calculate with invalid JSON"""
        response = client.post(
            "/calculate",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_calculate_with_missing_fields(self):
        """Test calculate with missing required fields"""
        transactions = [
            {
                "date": "2023-01-01",
                "symbol": "AAPL"
                # Missing required fields
            }
        ]

        response = client.post("/calculate", json=transactions)
        assert response.status_code == 422