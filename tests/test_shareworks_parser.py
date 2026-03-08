from backend.parsers.shareworks_parser import parse
from datetime import date
import tempfile
import csv
import os


def test_parse_valid_shareworks_file():
    """Test parsing a valid Shareworks CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-01-15', 'RSU', 'GOOGL', '10', '95.50'])
        writer.writerow(['2023-06-20', 'SELL', 'GOOGL', '5', '120.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 2

        # Check first transaction
        assert transactions[0].date == date(2023, 1, 15)
        assert transactions[0].transaction_type == 'RSU'
        assert transactions[0].symbol == 'GOOGL'
        assert transactions[0].shares == 10.0
        assert transactions[0].price == 95.50
        assert transactions[0].currency == 'USD'
        assert transactions[0].broker == 'Shareworks'

        # Check second transaction
        assert transactions[1].date == date(2023, 6, 20)
        assert transactions[1].transaction_type == 'SELL'
        assert transactions[1].shares == 5.0
        assert transactions[1].price == 120.00
    finally:
        os.unlink(temp_file)


def test_parse_empty_file():
    """Test parsing an empty Shareworks CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        # No data rows
        temp_file = f.name

    try:
        transactions = parse(temp_file)
        assert len(transactions) == 0
    finally:
        os.unlink(temp_file)


def test_parse_multiple_symbols():
    """Test parsing file with multiple different symbols"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-07-01', 'RSU', 'GOOGL', '10', '95.00'])
        writer.writerow(['2023-07-15', 'RSU', 'AAPL', '15', '150.00'])
        writer.writerow(['2023-08-01', 'RSU', 'MSFT', '20', '280.00'])
        writer.writerow(['2023-08-15', 'SELL', 'GOOGL', '5', '100.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 4
        symbols = [t.symbol for t in transactions]
        assert 'GOOGL' in symbols
        assert 'AAPL' in symbols
        assert 'MSFT' in symbols
    finally:
        os.unlink(temp_file)


def test_parse_different_plan_types():
    """Test parsing file with different plan types"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-09-01', 'RSU', 'NFLX', '10', '350.00'])
        writer.writerow(['2023-09-10', 'ESPP', 'NFLX', '5', '340.00'])
        writer.writerow(['2023-09-20', 'Stock Option', 'NFLX', '15', '330.00'])
        writer.writerow(['2023-09-30', 'SELL', 'NFLX', '8', '360.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 4
        plan_types = [t.transaction_type for t in transactions]
        assert 'RSU' in plan_types
        assert 'ESPP' in plan_types
        assert 'Stock Option' in plan_types
        assert 'SELL' in plan_types
    finally:
        os.unlink(temp_file)


def test_parse_date_formats():
    """Test parsing handles various date formats"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-10-15', 'RSU', 'AMZN', '10', '130.00'])
        writer.writerow(['10/20/2023', 'RSU', 'AMZN', '5', '135.00'])
        writer.writerow(['2023/10/25', 'SELL', 'AMZN', '3', '140.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        # pandas should handle different date formats
        assert len(transactions) >= 1
        assert transactions[0].date == date(2023, 10, 15)
    finally:
        os.unlink(temp_file)


def test_parse_zero_values():
    """Test parsing handles zero shares and prices"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-11-01', 'RSU', 'NVDA', '0', '450.00'])
        writer.writerow(['2023-11-02', 'RSU', 'NVDA', '25', '0'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        # Should parse rows even with zero values
        assert len(transactions) == 2
        assert transactions[0].shares == 0.0
        assert transactions[1].price == 0.0
    finally:
        os.unlink(temp_file)


def test_parse_decimal_shares():
    """Test parsing handles fractional shares"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2023-12-01', 'RSU', 'META', '10.5', '300.00'])
        writer.writerow(['2023-12-05', 'SELL', 'META', '5.25', '310.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 2
        assert transactions[0].shares == 10.5
        assert transactions[1].shares == 5.25
    finally:
        os.unlink(temp_file)


def test_parse_currency_defaults_to_usd():
    """Test that all transactions default to USD currency"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2024-01-10', 'RSU', 'INTC', '30', '45.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 1
        assert transactions[0].currency == 'USD'
    finally:
        os.unlink(temp_file)


def test_parse_large_price_values():
    """Test parsing handles large price values"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2024-02-01', 'RSU', 'BRK.A', '1', '525000.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 1
        assert transactions[0].price == 525000.00
    finally:
        os.unlink(temp_file)


def test_parse_negative_values():
    """Test parsing handles negative values (edge case for returns/corrections)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['Transaction Date', 'Plan Type', 'Symbol', 'Shares', 'Price'])
        writer.writerow(['2024-03-01', 'CORRECTION', 'AMD', '-5', '180.00'])
        temp_file = f.name

    try:
        transactions = parse(temp_file)

        assert len(transactions) == 1
        assert transactions[0].shares == -5.0
    finally:
        os.unlink(temp_file)