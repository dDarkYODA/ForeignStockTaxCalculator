import time
import io
import pandas as pd
import requests
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./benchmark.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db

def run_benchmark(num_transactions=1000):
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    # Generate large CSV
    data = []
    for i in range(num_transactions):
        data.append({
            'Transaction Date': '2023-01-15',
            'Plan Type': 'RSU',
            'Symbol': f'STOCK{i}',
            'Shares': 10,
            'Price': 100.0
        })
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)

    start_time = time.time()
    response = client.post(
        "/api/upload?broker=shareworks",
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    end_time = time.time()

    if response.status_code != 200:
        print(f"Error: {response.text}")
        return None

    duration = end_time - start_time
    print(f"Processed {num_transactions} transactions in {duration:.4f} seconds")

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    return duration

if __name__ == "__main__":
    print("Running baseline benchmark...")
    durations = []
    for _ in range(5):
        dur = run_benchmark(2000)
        if dur:
            durations.append(dur)

    if durations:
        avg_dur = sum(durations) / len(durations)
        print(f"Average duration: {avg_dur:.4f} seconds")
