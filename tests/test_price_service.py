from backend.services.price_service import price_service

def test_get_current_price_with_manual_price():
    """Test that get_current_price returns manual_price when provided"""
    symbol = "AAPL"
    manual_price = 150.0
    price = price_service.get_current_price(symbol, manual_price=manual_price)
    assert price == 150.0

def test_get_current_price_without_manual_price():
    """Test that get_current_price returns 0.0 when no manual_price is provided"""
    symbol = "GOOGL"
    price = price_service.get_current_price(symbol)
    assert price == 0.0

def test_get_current_price_with_different_symbols():
    """Test that get_current_price handles different symbols"""
    assert price_service.get_current_price("MSFT", manual_price=200.0) == 200.0
    assert price_service.get_current_price("TSLA") == 0.0

def test_get_current_price_manual_price_zero():
    """Test that get_current_price returns 0.0 if manual_price is explicitly 0.0"""
    assert price_service.get_current_price("AAPL", manual_price=0.0) == 0.0

def test_get_current_price_with_explicit_none():
    """
    Test calling price_service.get_current_price with manual_price=None.
    This mirrors the call path in portfolio_service.py where manual_prices.get(symbol)
    is passed, which may return None if the symbol is not in the dictionary.
    """
    assert price_service.get_current_price("GOOGL", manual_price=None) == 0.0
