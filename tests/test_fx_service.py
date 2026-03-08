import pytest
from datetime import date
from backend.services.fx_service import get_tt_buy_rate


class TestFXService:
    """Tests for FX rate service"""

    def test_get_tt_buy_rate_usd_exact_date(self):
        """Test fetching USD rate for exact date in cache"""
        rate = get_tt_buy_rate('USD', date(2023, 1, 1))
        assert rate == 82.5

    def test_get_tt_buy_rate_usd_different_dates(self):
        """Test fetching USD rates for different cached dates"""
        assert get_tt_buy_rate('USD', date(2023, 2, 1)) == 82.0
        assert get_tt_buy_rate('USD', date(2023, 3, 1)) == 82.2
        assert get_tt_buy_rate('USD', date(2024, 1, 1)) == 83.0

    def test_get_tt_buy_rate_inr(self):
        """Test INR always returns 1.0"""
        rate = get_tt_buy_rate('INR', date(2023, 1, 1))
        assert rate == 1.0

        rate = get_tt_buy_rate('INR', date(2025, 12, 31))
        assert rate == 1.0

    def test_get_tt_buy_rate_nearest_date_fallback(self):
        """Test fallback to nearest date when exact date not in cache"""
        # Should find nearest date in cache
        rate = get_tt_buy_rate('USD', date(2023, 1, 15))
        assert rate in [82.0, 82.2, 82.5, 83.0]  # Should return one of cached values

    def test_get_tt_buy_rate_future_date(self):
        """Test fetching rate for future date uses nearest cached date"""
        rate = get_tt_buy_rate('USD', date(2025, 1, 1))
        # Should return a cached value as fallback
        assert rate in [82.0, 82.2, 82.5, 83.0]

    def test_get_tt_buy_rate_past_date(self):
        """Test fetching rate for old date uses nearest cached date"""
        rate = get_tt_buy_rate('USD', date(2020, 1, 1))
        # Should return a cached value as fallback
        assert rate in [82.0, 82.2, 82.5, 83.0]

    def test_get_tt_buy_rate_unsupported_currency_default(self):
        """Test unsupported currency returns default fallback"""
        rate = get_tt_buy_rate('EUR', date(2023, 1, 1))
        assert rate == 83.0  # Default fallback

    def test_get_tt_buy_rate_empty_currency(self):
        """Test empty currency returns default"""
        rate = get_tt_buy_rate('', date(2023, 1, 1))
        assert rate == 83.0

    def test_get_tt_buy_rate_none_like_currency(self):
        """Test handling of unusual currency codes"""
        rate = get_tt_buy_rate('XXX', date(2023, 1, 1))
        assert rate == 83.0

    def test_get_tt_buy_rate_consistency(self):
        """Test that same inputs return same outputs"""
        rate1 = get_tt_buy_rate('USD', date(2023, 1, 1))
        rate2 = get_tt_buy_rate('USD', date(2023, 1, 1))
        assert rate1 == rate2

    def test_get_tt_buy_rate_case_sensitivity(self):
        """Test currency code case sensitivity"""
        # Service expects uppercase
        rate_upper = get_tt_buy_rate('USD', date(2023, 1, 1))
        rate_lower = get_tt_buy_rate('usd', date(2023, 1, 1))

        # Lower case should return default since key doesn't match
        assert rate_upper == 82.5
        assert rate_lower == 83.0

    def test_get_tt_buy_rate_boundary_dates(self):
        """Test rates at year boundaries"""
        # Start of 2023
        rate_2023 = get_tt_buy_rate('USD', date(2023, 1, 1))
        assert rate_2023 == 82.5

        # Start of 2024
        rate_2024 = get_tt_buy_rate('USD', date(2024, 1, 1))
        assert rate_2024 == 83.0

    def test_get_tt_buy_rate_returns_float(self):
        """Test that all returns are float type"""
        rate_usd = get_tt_buy_rate('USD', date(2023, 1, 1))
        rate_inr = get_tt_buy_rate('INR', date(2023, 1, 1))
        rate_unknown = get_tt_buy_rate('GBP', date(2023, 1, 1))

        assert isinstance(rate_usd, float)
        assert isinstance(rate_inr, float)
        assert isinstance(rate_unknown, float)