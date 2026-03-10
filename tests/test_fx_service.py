from backend.services.fx_service import fx_service
from datetime import date

get_tt_buy_rate = fx_service.get_tt_buy_rate

def test_get_tt_buy_rate_usd_exact_date():
    """Test getting TT buy rate for USD with exact date match in cache"""
    assert get_tt_buy_rate('USD', date(2023, 1, 15)) == 81.50
    assert get_tt_buy_rate('USD', date(2023, 6, 20)) == 82.10

def test_get_tt_buy_rate_usd_different_dates():
    """Test getting TT buy rate for USD falling back to year base"""
    assert get_tt_buy_rate('USD', date(2023, 2, 1)) == 82.5
    assert get_tt_buy_rate('USD', date(2023, 3, 1)) == 82.5
    assert get_tt_buy_rate('USD', date(2024, 1, 1)) == 83.2

def test_get_tt_buy_rate_inr_returns_one():
    """Test that INR always returns 1.0 (no conversion needed)"""
    rate = get_tt_buy_rate('INR', date(2023, 1, 1))
    assert rate == 1.0

    # Should always be 1.0 regardless of date
    assert get_tt_buy_rate('INR', date(2024, 12, 31)) == 1.0

def test_get_tt_buy_rate_future_date_fallback():
    """Test fallback for future dates not in cache"""
    rate = get_tt_buy_rate('USD', date(2025, 6, 15))
    assert rate == 83.0 # default rate

def test_get_tt_buy_rate_past_date_fallback():
    """Test fallback for past dates not in cache"""
    rate = get_tt_buy_rate('USD', date(2020, 1, 1))
    assert rate == 83.0

def test_get_tt_buy_rate_unknown_currency_default():
    """Test default fallback rate for unknown currency"""
    # For non-USD currency that gets upper() matched, it should return year-based or default
    rate = get_tt_buy_rate('EUR', date(2023, 1, 1))
    assert rate == 82.5 # year 2023 base

def test_get_tt_buy_rate_unknown_currency_various_dates():
    """Test unknown currency returns year base"""
    assert get_tt_buy_rate('GBP', date(2023, 1, 1)) == 82.5
    assert get_tt_buy_rate('JPY', date(2024, 6, 15)) == 83.2
    assert get_tt_buy_rate('CAD', date(2020, 12, 31)) == 83.0

def test_get_tt_buy_rate_consistency():
    """Test that same date always returns same rate"""
    rate1 = get_tt_buy_rate('USD', date(2023, 1, 1))
    rate2 = get_tt_buy_rate('USD', date(2023, 1, 1))

    assert rate1 == rate2
    assert rate1 == 82.5

def test_get_tt_buy_rate_case_sensitivity():
    """Test that currency code is case-insensitive (converts to upper)"""
    assert get_tt_buy_rate('usd', date(2023, 1, 15)) == 81.50

def test_get_tt_buy_rate_return_type():
    """Test that function always returns a float"""
    rate = get_tt_buy_rate('USD', date(2023, 1, 1))
    assert isinstance(rate, float)

    rate_inr = get_tt_buy_rate('INR', date(2023, 1, 1))
    assert isinstance(rate_inr, float)

    rate_unknown = get_tt_buy_rate('XXX', date(2023, 1, 1))
    assert isinstance(rate_unknown, float)

def test_get_tt_buy_rate_positive_values():
    """Test that all returned rates are positive"""
    rates = [
        get_tt_buy_rate('USD', date(2023, 1, 1)),
        get_tt_buy_rate('INR', date(2023, 1, 1)),
        get_tt_buy_rate('EUR', date(2023, 1, 1)),
    ]

    for rate in rates:
        assert rate > 0
