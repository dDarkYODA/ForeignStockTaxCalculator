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
        if currency.strip().upper() == "INR":
            return 1.0

        rate = self._cache.get((dt, currency.strip().upper()))
        if rate is not None:
            return rate

        # Get base USD rate for the year
        year_rates = {
            2021: 74.5,
            2022: 78.2,
            2023: 82.5,
            2024: 83.2
        }
        usd_rate = year_rates.get(dt.year, self.default_rate)

        multiplier = self.currency_multipliers.get(currency.strip().upper(), 1.0)
        return usd_rate * multiplier

fx_service = FXService()
