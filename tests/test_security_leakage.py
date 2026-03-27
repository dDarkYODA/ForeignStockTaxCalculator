
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch

client = TestClient(app)

def test_upload_no_error_leakage(capsys):
    """
    Test that the /api/upload endpoint does not leak error details to stdout.
    """
    with patch('backend.api.endpoints.parse_shareworks') as mock_parser:
        mock_parser.side_effect = Exception("SECRET_SENSITIVE_DATA")

        import io
        import csv

        content = io.StringIO()
        writer = csv.writer(content)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-01-15', 'RSU', 'GOOGL', '10', '95.50'])

        response = client.post(
            "/api/upload?broker=shareworks",
            files={"file": ("test.csv", content.getvalue(), "text/csv")}
        )

        assert response.status_code == 500
        captured = capsys.readouterr()
        assert "SECRET_SENSITIVE_DATA" not in captured.out
        assert "SECRET_SENSITIVE_DATA" not in response.text

def test_simulate_trade_no_error_leakage(capsys):
    """
    Test that the /api/simulate-trade endpoint does not leak error details to stdout.
    """
    with patch('backend.api.endpoints.simulate_trade') as mock_simulate:
        mock_simulate.side_effect = Exception("SENSITIVE_SIMULATION_ERROR")

        payload = {
            "symbol": "AAPL",
            "shares": 10,
            "price": 150.0,
            "currency": "USD",
            "date": "2023-01-01"
        }

        response = client.post("/api/simulate-trade", json=payload)

        assert response.status_code == 500
        captured = capsys.readouterr()
        assert "SENSITIVE_SIMULATION_ERROR" not in captured.out
        assert "SENSITIVE_SIMULATION_ERROR" not in response.text
