from backend.models.transaction import Transaction

def match_lots(transactions: list[Transaction]) -> list[tuple[Transaction, Transaction, float]]:
    """
    Match BUY/VEST transactions with SELL transactions using FIFO.
    Returns a list of tuples: (buy_transaction, sell_transaction, matched_shares)
    """
    matches = []
    
    # Sort by date
    transactions = sorted(transactions, key=lambda x: x.date)
    
    # Track inventory (buy/vest lots)
    inventory = []
    
    for t in transactions:
        if t.transaction_type in ['BUY', 'RSU_VEST', 'ESPP_PURCHASE']:
            inventory.append({
                'tx': t,
                'remaining': t.shares
            })
        elif t.transaction_type == 'SELL':
            shares_to_sell = t.shares
            
            # Consume inventory
            while shares_to_sell > 0 and inventory:
                lot = inventory[0]
                available = lot['remaining']
                
                if available <= shares_to_sell:
                    matches.append((lot['tx'], t, available))
                    shares_to_sell -= available
                    inventory.pop(0)
                else:
                    matches.append((lot['tx'], t, shares_to_sell))
                    lot['remaining'] -= shares_to_sell
                    shares_to_sell = 0
                    
    return matches
