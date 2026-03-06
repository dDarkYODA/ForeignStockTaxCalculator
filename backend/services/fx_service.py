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
        self.default_rate = 83.0  # fallback

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
            
        # For dates not in mock cache, return a deterministic derived value based on year
        if dt.year == 2021: return 74.5
        if dt.year == 2022: return 78.2
        if dt.year == 2023: return 82.5
        if dt.year == 2024: return 83.2
        
        return self.default_rate

fx_service = FXService()
