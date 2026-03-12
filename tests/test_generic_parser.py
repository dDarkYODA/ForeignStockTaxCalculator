import pytest
from backend.models.schema import TransactionType
import pandas as pd
from backend.parsers.generic_parser import infer_schema_with_ai, parse_generic_with_mapping
parse = parse_generic_with_mapping
infer_schema = infer_schema_with_ai
import tempfile
import csv
import os
import pandas as pd


def test_infer_schema_fallback_basic():
    """Test schema inference with fallback logic (no OpenAI key)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Trade Date', 'Plan Type', 'Ticker', 'Amount', 'Value', 'Currency'])
        writer.writerow(['2023-01-15', 'Buy', 'GOOGL', '10', '95.50', 'USD'])
        temp_file = f.name

    try:
        # Without OPENAI_API_KEY, it should use fallback mapping
        old_key = os.environ.get('OPENAI_API_KEY')
        if old_key:
            del os.environ['OPENAI_API_KEY']

        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
    finally:
        os.unlink(temp_file)



def test_parse_sets_default_broker():
    """Test that parsed transactions have 'Unknown' broker set"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'type', 'symbol', 'shares', 'price', 'currency'])
        writer.writerow(['2023-07-15', 'Buy', 'NVDA', '25', '450.00', 'USD'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
        transactions = parse(df, mapping=schema)

        assert len(transactions) == 1
        assert transactions[0]['broker'] == 'Generic'
    finally:
        os.unlink(temp_file)


def test_parse_handles_empty_file():
    """Test parsing an empty CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'type', 'symbol', 'shares', 'price', 'currency'])
        # No data rows
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
        transactions = parse(df, mapping=schema)
        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)


def test_infer_schema_with_instrument_column():
    """Test schema inference recognizes 'instrument' as symbol"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Type', 'Instrument', 'Shares', 'Price'])
        writer.writerow(['2023-08-01', 'Buy', 'META', '10', '300.00'])
        temp_file = f.name

    try:
        old_key = os.environ.get('OPENAI_API_KEY')
        if old_key:
            del os.environ['OPENAI_API_KEY']

        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))

    finally:
        os.unlink(temp_file)
        if old_key:
            os.environ['OPENAI_API_KEY'] = old_key


def test_parse_with_cost_basis_column():
    """Test parsing with 'Cost Basis' column mapping to price"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Trade Date', 'Action', 'Security', 'Shares', 'Cost Basis', 'Currency'])
        writer.writerow(['2023-09-10', 'Buy', 'AMZN', '8', '130.00', 'USD'])
        temp_file = f.name

    try:
        old_key = os.environ.get('OPENAI_API_KEY')
        if old_key:
            del os.environ['OPENAI_API_KEY']

        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
        transactions = parse(df, mapping=schema)

        assert len(transactions) == 1
        # Cost Basis should map to price
        assert transactions[0]['price'] == 130.0
    finally:
        os.unlink(temp_file)
        if old_key:
            os.environ['OPENAI_API_KEY'] = old_key


def test_parse_defaults_to_usd_currency():
    """Test that parser defaults to USD when currency column is missing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'type', 'symbol', 'shares', 'price'])
        writer.writerow(['2023-10-01', 'Buy', 'GOOG', '12', '140.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
        transactions = parse(df, mapping=schema)

        assert len(transactions) == 1
        assert transactions[0]['currency'] == 'USD'
    finally:
        os.unlink(temp_file)


def test_parse_handles_zero_values():
    """Test parsing handles zero shares and prices"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'type', 'symbol', 'shares', 'price', 'currency'])
        writer.writerow(['2023-11-01', 'Buy', 'INTC', '0', '45.00', 'USD'])
        writer.writerow(['2023-11-02', 'Buy', 'INTC', '10', '0', 'USD'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        schema = infer_schema(list(df.columns), df.head(20).to_dict(orient="records"))
        transactions = parse(df, mapping=schema)

        # Should parse rows even with zero values
        assert len(transactions) == 2
        assert transactions[0]['shares'] == 0.0
        assert transactions[1]['price'] == 0.0
    finally:
        os.unlink(temp_file)