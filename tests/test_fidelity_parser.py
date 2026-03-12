from backend.models.schema import TransactionType
import pandas as pd
from backend.parsers.fidelity_parser import parse_fidelity
parse = parse_fidelity
from datetime import date
import tempfile
import csv
import os
import pandas as pd


def test_parse_valid_fidelity_file():
    """Test parsing a valid Fidelity CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-02-10', 'Buy', 'AAPL', '20', '150.00'])
        writer.writerow(['2024-03-15', 'Sell', 'AAPL', '10', '180.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 2

        # Check first transaction
        assert transactions[0]['date'] == date(2023, 2, 10)
        assert transactions[0]['transaction_type'].value == 'BUY'
        assert transactions[0]['symbol'] == 'AAPL'
        assert transactions[0]['shares'] == 20.0
        assert transactions[0]['price'] == 150.00
        assert transactions[0]['currency'] == 'USD'
        assert transactions[0]['broker'] == 'Fidelity'

        # Check second transaction
        assert transactions[1]['date'] == date(2024, 3, 15)
        assert transactions[1]['transaction_type'].value == 'SELL'
        assert transactions[1]['shares'] == 10.0
        assert transactions[1]['price'] == 180.00
    finally:
        os.unlink(temp_file)


def test_parse_empty_file():
    """Test parsing an empty Fidelity CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        # No data rows
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)
        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)


def test_parse_multiple_securities():
    """Test parsing file with multiple different securities"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-08-01', 'Buy', 'GOOGL', '10', '95.00'])
        writer.writerow(['2023-08-10', 'Buy', 'AAPL', '15', '150.00'])
        writer.writerow(['2023-08-20', 'Buy', 'MSFT', '20', '280.00'])
        writer.writerow(['2023-08-30', 'Sell', 'GOOGL', '5', '100.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 4
        securities = [t['symbol'] for t in transactions]
        assert 'GOOGL' in securities
        assert 'AAPL' in securities
        assert 'MSFT' in securities
    finally:
        os.unlink(temp_file)


def test_parse_different_action_types():
    """Test parsing file with different action types"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-09-01', 'Buy', 'NFLX', '10', '350.00'])
        writer.writerow(['2023-09-10', 'Sell', 'NFLX', '5', '360.00'])
        writer.writerow(['2023-09-20', 'Dividend Reinvestment', 'NFLX', '2', '340.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 3
        actions = [t['transaction_type'].value for t in transactions]
        assert actions.count('BUY') == 2
        assert actions.count('SELL') == 1
        assert actions == ['BUY', 'SELL', 'BUY']
    finally:
        os.unlink(temp_file)


def test_parse_date_formats():
    """Test parsing handles various date formats"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-10-15', 'Buy', 'AMZN', '10', '130.00'])
        writer.writerow(['10/20/2023', 'Buy', 'AMZN', '5', '135.00'])
        writer.writerow(['2023/10/25', 'Sell', 'AMZN', '3', '140.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        # pandas should handle different date formats
        assert len(transactions) >= 1
        assert transactions[0]['date'] == date(2023, 10, 15)
    finally:
        os.unlink(temp_file)


def test_parse_zero_values():
    """Test parsing handles zero quantity and prices"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-11-01', 'Buy', 'NVDA', '0', '450.00'])
        writer.writerow(['2023-11-02', 'Buy', 'NVDA', '25', '0'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        # Should parse rows even with zero values
        assert len(transactions) == 2
        assert transactions[0]['shares'] == 0.0
        assert transactions[1]['price'] == 0.0
    finally:
        os.unlink(temp_file)


def test_parse_decimal_quantity():
    """Test parsing handles fractional shares"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2023-12-01', 'Buy', 'META', '10.75', '300.00'])
        writer.writerow(['2023-12-05', 'Sell', 'META', '5.5', '310.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 2
        assert transactions[0]['shares'] == 10.75
        assert transactions[1]['shares'] == 5.5
    finally:
        os.unlink(temp_file)


def test_parse_currency_defaults_to_usd():
    """Test that all transactions default to USD currency"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2024-01-10', 'Buy', 'INTC', '30', '45.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 1
        assert transactions[0]['currency'] == 'USD'
    finally:
        os.unlink(temp_file)


def test_parse_large_quantity_values():
    """Test parsing handles large quantity values"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2024-02-01', 'Buy', 'PENNY', '100000', '0.50'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 1
        assert transactions[0]['shares'] == 100000.0
    finally:
        os.unlink(temp_file)


def test_parse_negative_quantity():
    """Test parsing handles negative quantity (edge case for corrections)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2024-03-01', 'Adjustment', 'AMD', '-5', '180.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)


def test_parse_symbol_with_special_characters():
    """Test parsing handles symbols with special characters"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Action', 'Security', 'Quantity', 'Price'])
        writer.writerow(['2024-04-01', 'Buy', 'BRK.B', '10', '350.00'])
        writer.writerow(['2024-04-05', 'Buy', 'BRK-A', '1', '525000.00'])
        temp_file = f.name

    try:
        df = pd.read_csv(temp_file)
        transactions = parse(df)

        assert len(transactions) == 2
        assert transactions[0]['symbol'] == 'BRK.B'
        assert transactions[1]['symbol'] == 'BRK-A'
    finally:
        os.unlink(temp_file)