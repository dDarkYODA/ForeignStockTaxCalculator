import re

with open("tests/test_main.py", "r") as f:
    content = f.read()

# Fix shareworks valid test
content = content.replace(
"""        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'GOOGL'
        assert transactions[0]['broker'] == 'Shareworks'""",
"""        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify saved transactions
        tx_res = client.get("/api/transactions")
        transactions = tx_res.json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'GOOGL'
        assert transactions[0]['broker'] == 'Shareworks'"""
)

# Fix fidelity valid test
content = content.replace(
"""        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'AAPL'
        assert transactions[0]['broker'] == 'Fidelity'""",
"""        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify saved transactions
        tx_res = client.get("/api/transactions")
        transactions = tx_res.json()
        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'AAPL'
        assert transactions[0]['broker'] == 'Fidelity'"""
)

# Fix generic parser upload
content = content.replace(
"""                    "/api/upload?broker=unknown",""",
"""                    "/api/upload?broker=generic","""
)
content = content.replace(
"""        assert response.status_code == 200
        transactions = response.json()
        # Generic parser should work even without API key (uses fallback)
        assert len(transactions) >= 0""",
"""        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "requires_mapping"
        assert "inferred_mapping" in data"""
)

# Fix empty csv test
content = content.replace(
"""        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 0""",
"""        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify saved transactions
        tx_res = client.get("/api/transactions")
        transactions = tx_res.json()
        assert len(transactions) == 0"""
)

with open("tests/test_main.py", "w") as f:
    f.write(content)
