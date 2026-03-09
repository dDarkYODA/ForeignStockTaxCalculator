class PriceService:
    def __init__(self):
        pass

    def get_current_price(self, symbol: str, manual_price: float = None) -> float:
        """
        Returns the current price for a symbol.
        For MVP, it heavily relies on manual_price input.
        If manual_price is provided, it returns that.
        Otherwise, it returns a default of 0.0.
        """
        if manual_price is not None:
            return manual_price

        # In the future, integrate yfinance, alpha_vantage, or polygon here
        return 0.0

price_service = PriceService()
