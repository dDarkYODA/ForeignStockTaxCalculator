import re

with open('backend/services/trade_simulator.py', 'r') as f:
    content = f.read()

# Add func to imports
if 'from sqlalchemy import func' not in content:
    content = 'from sqlalchemy import func\n' + content

bad_block = """    available_lots = db.query(Lot).filter(
        Lot.user_id == user_id,
        Lot.symbol == symbol,
        Lot.available_shares > 0
    ).order_by(Lot.date).all()"""

good_block = """    available_lots = db.query(Lot).filter(
        Lot.user_id == user_id,
        func.lower(Lot.symbol) == symbol.lower(),
        Lot.available_shares > 0
    ).order_by(Lot.date).all()"""

content = content.replace(bad_block, good_block)

with open('backend/services/trade_simulator.py', 'w') as f:
    f.write(content)
