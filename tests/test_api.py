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


def test_calculate_tax_multiple_symbols():
    """Test calculating tax for multiple different symbols"""
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
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "GOOGL",
            "shares": 5,
            "price": 2000.0,
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
        },
        {
            "date": "2023-07-01",
            "transaction_type": "SELL",
            "symbol": "GOOGL",
            "shares": 2,
            "price": 2200.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 2
    symbols = [r["symbol"] for r in results]
    assert "AAPL" in symbols
    assert "GOOGL" in symbols


def test_calculate_tax_partial_sales():
    """Test multiple partial sales from same lot"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "TSLA",
            "shares": 100,
            "price": 200.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-03-01",
            "transaction_type": "SELL",
            "symbol": "TSLA",
            "shares": 30,
            "price": 220.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-05-01",
            "transaction_type": "SELL",
            "symbol": "TSLA",
            "shares": 40,
            "price": 210.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 2
    total_shares_sold = sum(r["shares"] for r in results)
    assert total_shares_sold == 70


def test_calculate_tax_exact_24_months_boundary():
    """Test exactly 24 months holding should be STCG"""
    transactions = [
        {
            "date": "2020-01-01",
            "transaction_type": "BUY",
            "symbol": "NFLX",
            "shares": 10,
            "price": 300.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2022-01-01",
            "transaction_type": "SELL",
            "symbol": "NFLX",
            "shares": 10,
            "price": 400.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    # Exactly 24 months should be STCG (needs > 24 months for LTCG)
    assert results[0]["holding_type"] == "STCG"


def test_calculate_tax_over_24_months():
    """Test just over 24 months should be LTCG"""
    transactions = [
        {
            "date": "2020-01-01",
            "transaction_type": "BUY",
            "symbol": "AMZN",
            "shares": 10,
            "price": 1800.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2022-02-01",
            "transaction_type": "SELL",
            "symbol": "AMZN",
            "shares": 10,
            "price": 3000.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    assert results[0]["holding_type"] == "LTCG"


def test_calculate_tax_negative_gain():
    """Test calculating tax when price goes down (loss)"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "META",
            "shares": 10,
            "price": 300.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-06-01",
            "transaction_type": "SELL",
            "symbol": "META",
            "shares": 10,
            "price": 250.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    assert results[0]["gain_inr"] < 0  # Loss


def test_calculate_tax_rsu_vest():
    """Test RSU vesting transactions"""
    transactions = [
        {
            "date": "2022-01-01",
            "transaction_type": "RSU_VEST",
            "symbol": "MSFT",
            "shares": 50,
            "price": 250.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-03-01",
            "transaction_type": "SELL",
            "symbol": "MSFT",
            "shares": 25,
            "price": 280.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    assert results[0]["holding_type"] == "STCG"


def test_calculate_tax_fifo_order():
    """Test FIFO ordering with multiple buys"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "IBM",
            "shares": 10,
            "price": 100.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-02-01",
            "transaction_type": "BUY",
            "symbol": "IBM",
            "shares": 10,
            "price": 110.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-03-01",
            "transaction_type": "SELL",
            "symbol": "IBM",
            "shares": 15,
            "price": 120.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    # Should create 2 matches: 10 from first buy, 5 from second buy
    assert len(results) == 2


def test_calculate_tax_fractional_shares():
    """Test handling fractional shares"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "BRK.B",
            "shares": 10.5,
            "price": 300.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-06-01",
            "transaction_type": "SELL",
            "symbol": "BRK.B",
            "shares": 5.25,
            "price": 320.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    assert results[0]["shares"] == 5.25


def test_calculate_tax_inr_currency():
    """Test transactions already in INR"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "TCS",
            "shares": 10,
            "price": 3000.0,
            "currency": "INR",
            "broker": "Test"
        },
        {
            "date": "2023-06-01",
            "transaction_type": "SELL",
            "symbol": "TCS",
            "shares": 10,
            "price": 3500.0,
            "currency": "INR",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    # For INR, FX rate should be 1.0
    assert results[0]["cost_inr"] == 10 * 3000.0 * 1.0
    assert results[0]["sale_inr"] == 10 * 3500.0 * 1.0


def test_calculate_tax_zero_price():
    """Test handling zero price (e.g., free stock)"""
    transactions = [
        {
            "date": "2023-01-01",
            "transaction_type": "BUY",
            "symbol": "FREE",
            "shares": 10,
            "price": 0.0,
            "currency": "USD",
            "broker": "Test"
        },
        {
            "date": "2023-06-01",
            "transaction_type": "SELL",
            "symbol": "FREE",
            "shares": 10,
            "price": 50.0,
            "currency": "USD",
            "broker": "Test"
        }
    ]

    response = client.post("/calculate", json=transactions)
    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1
    # Cost should be zero, all sale proceeds are gain
    assert results[0]["cost_inr"] == 0.0
    assert results[0]["gain_inr"] > 0