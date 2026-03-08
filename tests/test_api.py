from fastapi.testclient import TestClient
from backend.main import app
from datetime import date

client = TestClient(app)

def test_calculate_tax_endpoint():
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
    assert results[0]["symbol"] == "AAPL"
    assert results[0]["shares"] == 5

def test_calculate_tax_ltcg():
    transactions = [
        {
            "date": "2021-01-01",
            "transaction_type": "BUY",
            "symbol": "MSFT",
            "shares": 20,
            "price": 200.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2024-01-01",
            "transaction_type": "SELL",
            "symbol": "MSFT",
            "shares": 20,
            "price": 300.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["holding_type"] == "LTCG"
    assert results[0]["symbol"] == "MSFT"
