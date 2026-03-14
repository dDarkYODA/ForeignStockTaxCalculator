from datetime import date
import pandas as pd
from typing import Dict, Tuple

class FXService:
    def __init__(self):
        # Mock historical FX cache (date, currency) -> rate
        self._cache: Dict[Tuple[date, str], float] = {
            (date(2023, 1, 15), "USD"): 81.50,
            (date(2023, 6, 20), "USD"): 82.10,
            (date(2024, 2, 10), "USD"): 83.00,
            (date(2024, 5, 5), "USD"): 83.50,
        }
        self.default_rate = 83.0  # fallback for USD

        # Multipliers relative to USD
        self.currency_multipliers = {
            "USD": 1.0,
            "EUR": 1.08,
            "GBP": 1.25,
            "CHF": 1.12,
            "CAD": 0.74,
            "AUD": 0.65,
            "JPY": 0.0067,
        }

    def get_tt_buy_rate(self, currency: str, dt: date) -> float:
        """
        Mock implementation of SBI TT buying rate.
        In a real app, this would query an API or a database of historical rates.
        """
        if currency.upper() == "INR":
            return 1.0

        rate = self._cache.get((dt, currency.upper()))
        if rate is not None:
            return rate

        # Get base USD rate for the year
        usd_rate = self.default_rate
        if dt.year == 2021: usd_rate = 74.5
        elif dt.year == 2022: usd_rate = 78.2
        elif dt.year == 2023: usd_rate = 82.5
        elif dt.year == 2024: usd_rate = 83.2

        multiplier = self.currency_multipliers.get(currency.upper(), 1.0)
        return usd_rate * multiplier

fx_service = FXService()
