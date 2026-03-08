import pandas as pd
import time
import os
from backend.parsers.shareworks_parser import parse as parse_shareworks
from backend.models.transaction import Transaction

def generate_dummy_data(filename, num_rows):
    """
    Create a CSV file containing synthetic Shareworks-style transaction rows.
    
    Generates a CSV at the given filename with num_rows rows and the following columns:
    'Transaction Date' (all '2023-01-01'), 'Plan Type' (all 'RSU_VEST'), 'Symbol' (all 'MSFT'),
    'Shares' (all 50.0), and 'Price' (all 250.0).
    
    Parameters:
        filename (str): Path where the CSV file will be written.
        num_rows (int): Number of synthetic rows to generate.
    """
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
    """
    Run a lightweight benchmark of the Shareworks parser using a generated CSV.
    
    Creates a temporary CSV at 'data/large_shareworks_dummy.csv' with 10,000 rows, invokes `parse_shareworks` on that file, prints the number of parsed rows and the elapsed time, and then removes the temporary file.
    """
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
