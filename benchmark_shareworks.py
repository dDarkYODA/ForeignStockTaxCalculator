import pandas as pd
import time
import os
from backend.parsers.shareworks_parser import parse as parse_shareworks
from backend.models.transaction import Transaction

def generate_dummy_data(filename, num_rows):
    data = {
        'Transaction Date': ['2023-01-01'] * num_rows,
        'Plan Type': ['RSU_VEST'] * num_rows,
        'Symbol': ['MSFT'] * num_rows,
        'Shares': [50.0] * num_rows,
        'Price': [250.0] * num_rows
    }
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def benchmark():
    dummy_file = 'data/large_shareworks_dummy.csv'
    num_rows = 10000
    generate_dummy_data(dummy_file, num_rows)

    start_time = time.time()
    transactions = parse_shareworks(dummy_file)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Parsed {len(transactions)} rows in {duration:.4f} seconds")

    # Cleanup
    if os.path.exists(dummy_file):
        os.remove(dummy_file)

if __name__ == "__main__":
    benchmark()
