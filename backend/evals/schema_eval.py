import os
import json
import braintrust
from braintrust import Eval
from backend.parsers.generic_parser import infer_schema

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../datasets/schema_inference')
EXPECTED_SCHEMAS_FILE = os.path.join(DATA_DIR, 'expected_schemas.json')

def load_data():
    if not os.path.exists(EXPECTED_SCHEMAS_FILE):
        return []
    with open(EXPECTED_SCHEMAS_FILE, 'r') as f:
        expected_schemas = json.load(f)

    data = []
    for file_name, expected_schema in expected_schemas.items():
        file_path = os.path.join(DATA_DIR, file_name)
        data.append({
            "input": file_path,
            "expected": expected_schema
        })
    return data

def task(input_data):
    file_path = input_data
    return infer_schema(file_path)

def accuracy_scorer(input, expected, output, **kwargs):
    correct = 0
    total = len(expected)
    for key, val in expected.items():
        if output.get(key) == val:
            correct += 1
    return correct / total if total > 0 else 0

def run_eval():
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    # If no API key is provided, log a warning and exit early.
    # Braintrust framework requires a valid key to login.
    if not api_key:
        print("Warning: BRAINTRUST_API_KEY is not set. Skipping evaluation.")
        return

    data = load_data()
    if not data:
        print("No evaluation data found. Skipping evaluation.")
        return

    Eval(
        "ForeignStockTaxCalculator",
        data=data,
        task=task,
        scores=[accuracy_scorer]
    )

if __name__ == '__main__':
    run_eval()
