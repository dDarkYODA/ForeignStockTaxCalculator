from datetime import date
from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    date: date
    transaction_type: str
    symbol: str
    shares: float
    price: float
    currency: str
    broker: str
    reference_id: Optional[str] = None

class TaxResult(BaseModel):
    date: date
    symbol: str
    shares: float
    cost_inr: float
    sale_inr: float
    gain_inr: float
    holding_type: str
