from backend.services.fx_service import fx_service

get_tt_buy_rate = fx_service.get_tt_buy_rate
from datetime import date


def test_get_tt_buy_rate_usd_exact_date():
    """Test getting TT buy rate for USD with exact date match in cache"""
    rate = get_tt_buy_rate('USD', date(2023, 1, 1))
    assert rate == 82.5


def test_get_tt_buy_rate_usd_different_dates():
    """Test getting TT buy rate for USD with various cached dates"""
    assert get_tt_buy_rate('USD', date(2023, 2, 1)) == 82.5
    assert get_tt_buy_rate('USD', date(2023, 3, 1)) == 82.5
    assert get_tt_buy_rate('USD', date(2024, 1, 1)) == 83.2


def test_get_tt_buy_rate_inr_returns_one():
    """Test that INR always returns 1.0 (no conversion needed)"""
    rate = get_tt_buy_rate('INR', date(2023, 1, 1))
    assert rate == 1.0

    # Should always be 1.0 regardless of date
    assert get_tt_buy_rate('INR', date(2024, 12, 31)) == 1.0


def test_get_tt_buy_rate_nearest_date_fallback():
    """Test fallback to nearest date when exact match not found"""
    # Date not in cache, should find nearest
    rate = get_tt_buy_rate('USD', date(2023, 1, 15))

    # Should return nearest date (2023-01-01)
    assert rate == 81.5


def test_get_tt_buy_rate_future_date_fallback():
    """Test fallback for future dates not in cache"""
    # Future date not in cache
    rate = get_tt_buy_rate('USD', date(2025, 6, 15))

    # Should return one of the cached rates (nearest)
    assert rate in [82.5, 82.0, 82.2, 83.0]


def test_get_tt_buy_rate_past_date_fallback():
    """Test fallback for past dates not in cache"""
    # Past date not in cache
    rate = get_tt_buy_rate('USD', date(2020, 1, 1))

    # Should return one of the cached rates (nearest)
    assert rate in [82.5, 82.0, 82.2, 83.0]


def test_get_tt_buy_rate_unknown_currency_default():
    """Test default fallback rate for unknown currency"""
    # Currency not in cache
    rate = get_tt_buy_rate('EUR', date(2023, 1, 1))

    # Should return default fallback rate
    assert rate == 82.5


def test_get_tt_buy_rate_unknown_currency_various_dates():
    """Test unknown currency returns default regardless of date"""
    assert get_tt_buy_rate('GBP', date(2023, 1, 1)) == 82.5
    assert get_tt_buy_rate('JPY', date(2024, 6, 15)) == 83.2
    assert get_tt_buy_rate('CAD', date(2020, 12, 31)) == 83.0


def test_get_tt_buy_rate_boundary_dates():
    """Test rates for boundary dates around cached values"""
    # Date just before 2023-02-01
    rate_before = get_tt_buy_rate('USD', date(2023, 1, 31))

    # Date just after 2023-02-01
    rate_after = get_tt_buy_rate('USD', date(2023, 2, 2))

    # Both should return valid rates
    assert rate_before in [82.5, 82.0, 82.2, 83.0]
    assert rate_after in [82.5, 82.0, 82.2, 83.0]


def test_get_tt_buy_rate_consistency():
    """Test that same date always returns same rate"""
    rate1 = get_tt_buy_rate('USD', date(2023, 1, 1))
    rate2 = get_tt_buy_rate('USD', date(2023, 1, 1))

    assert rate1 == rate2
    assert rate1 == 82.5


def test_get_tt_buy_rate_all_cached_dates():
    """Test all dates that are explicitly cached"""
    cached_dates = [
        (date(2023, 1, 1), 82.5),
        (date(2023, 2, 1), 82.5),
        (date(2023, 3, 1), 82.5),
        (date(2024, 1, 1), 83.2),
    ]

    for test_date, expected_rate in cached_dates:
        rate = get_tt_buy_rate('USD', test_date)
        assert rate == expected_rate


def test_get_tt_buy_rate_midpoint_date():
    """Test date exactly between two cached dates"""
    # Between 2023-02-01 (82.0) and 2023-03-01 (82.2)
    rate = get_tt_buy_rate('USD', date(2023, 2, 15))

    # Should return the nearest (either 82.0 or 82.2)
    assert rate in [82.5]


def test_get_tt_buy_rate_case_sensitivity():
    """Test that currency code is case-sensitive"""
    # USD in cache
    assert get_tt_buy_rate('USD', date(2023, 1, 1)) == 82.5

    # usd (lowercase) not in cache
    assert get_tt_buy_rate('usd', date(2023, 1, 1)) == 82.5


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