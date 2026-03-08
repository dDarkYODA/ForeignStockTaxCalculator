import pandas as pd
import time
import os
import random
import tempfile
from datetime import datetime, timedelta
from backend.parsers.shareworks_parser import parse as parse_shareworks

def generate_dummy_data(filename, num_rows):
    symbols = ['MSFT', 'GOOGL', 'AAPL', 'AMZN', 'TSLA']
    plan_types = ['RSU_VEST', 'SELL', 'OPTION_EXERCISE']

    data = {
        'Transaction Date': [
            (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            for _ in range(num_rows)
        ],
        'Plan Type': [random.choice(plan_types) for _ in range(num_rows)],
        'Symbol': [random.choice(symbols) for _ in range(num_rows)],
        'Shares': [round(random.uniform(1.0, 100.0), 2) for _ in range(num_rows)],
        'Price': [round(random.uniform(100.0, 1000.0), 2) for _ in range(num_rows)]
    }
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def benchmark():
    num_rows = 10000
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        dummy_path = tmp.name

    try:
        generate_dummy_data(dummy_path, num_rows)

        start_time = time.time()
        transactions = parse_shareworks(dummy_path)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Parsed {len(transactions)} rows in {duration:.4f} seconds")
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    benchmark()
