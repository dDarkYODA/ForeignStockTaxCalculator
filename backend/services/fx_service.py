from datetime import date
import pandas as pd

# Mock cache for FX rates
# In a real app this would fetch from an API or DB
_cache = {
    'USD': {
        date(2023, 1, 1): 82.5,
        date(2023, 2, 1): 82.0,
        date(2023, 3, 1): 82.2,
        date(2024, 1, 1): 83.0,
    }
}

def get_tt_buy_rate(currency: str, date_val: date) -> float:
    """
    Returns the SBI TT buying rate for a given currency on a given date.
    """
    if currency == 'INR':
        return 1.0
        
    rates = _cache.get(currency, {})
    if date_val in rates:
        return rates[date_val]
    
    # Simple fallback mechanism - find nearest date
    # Not ideal for production but good enough for this project setup
    if rates:
        closest_date = min(rates.keys(), key=lambda d: abs(d - date_val))
        return rates[closest_date]
        
    # Default fallback
    return 83.0
