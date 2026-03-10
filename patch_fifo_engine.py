import sys

def main():
    content = ""
    with open("backend/services/fifo_engine.py", "r") as f:
        content = f.read()

    # remove the currency fallback logic
    old_currency_logic = """        # Calculate costs and gains
        # Cost INR is calculated based on the FX rate at the time of purchase
        cost_fx_rate = fx_service.get_tt_buy_rate(lot.currency if hasattr(lot, 'currency') else 'USD', lot.date)
        cost_inr = shares_matched * lot.price * cost_fx_rate"""

    new_currency_logic = """        # Calculate costs and gains
        # Cost INR is prorated based on the lot's total cost_inr
        cost_inr = (lot.cost_inr / lot.shares) * shares_matched if lot.shares > 0 else 0"""

    content = content.replace(old_currency_logic, new_currency_logic)

    with open("backend/services/fifo_engine.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
