import re

with open("tests/test_main.py", "r") as f:
    content = f.read()

# Fix SQLALCHEMY_DATABASE_URL to be in-memory static pool
content = content.replace(
    'SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"\nengine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})',
    'SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"\nfrom sqlalchemy.pool import StaticPool\nengine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)'
)

# Remove duplicate test statements in test_upload_shareworks_valid
content = re.sub(
    r"        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)\n        response_data = response\.json\(\)\n        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)",
    "        assert response_data['status'] == 'success'\n        transactions = client.get('/api/transactions').json()",
    content
)

# Remove duplicate test statements in test_upload_fidelity_valid
content = re.sub(
    r"        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)\n        response_data = response\.json\(\)\n        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)",
    "        assert response_data['status'] == 'success'\n        transactions = client.get('/api/transactions').json()",
    content
)

# Remove duplicate test statements in test_upload_empty_csv
content = re.sub(
    r"        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)\n        response_data = response\.json\(\)\n        assert response_data\['status'\] == 'success'\n        transactions = client\.get\('/api/transactions'\)\.json\(\)",
    "        assert response_data['status'] == 'success'\n        transactions = client.get('/api/transactions').json()",
    content
)

with open("tests/test_main.py", "w") as f:
    f.write(content)
