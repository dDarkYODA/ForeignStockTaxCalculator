import sys

def main():
    content = ""
    with open("backend/services/portfolio_service.py", "r") as f:
        content = f.read()

    # remove the currency fallback logic
    old_currency_logic = """
        # We need a currency to get the fx rate for current value.
        # Since we aggregate by symbol, and typically a symbol has one currency,
        # we can just find one lot for this symbol to get its currency.
        # Let's query one lot to get the currency or assume USD.
        # Our Lot model currently doesn't persist `currency` explicitly (it was added dynamically in process_transactions).
        # We'll default to USD if we can't determine it, or we could add a `currency` column to `Lot`.
        currency = "USD"
        sample_lot = next((l for l in lots if l.symbol == symbol), None)
        if sample_lot and hasattr(sample_lot, 'currency') and sample_lot.currency:
            currency = sample_lot.currency
"""
    new_currency_logic = """
        currency = "USD" # Default in case no lots are found, but we shouldn't hit this
        sample_lot = next((l for l in lots if l.symbol == symbol), None)
        if sample_lot and sample_lot.currency:
            currency = sample_lot.currency
"""
    content = content.replace(old_currency_logic, new_currency_logic)

    with open("backend/services/portfolio_service.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
