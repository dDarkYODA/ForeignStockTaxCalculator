from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Index, func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    RSU_VEST = "RSU_VEST"
    ESPP_PURCHASE = "ESPP_PURCHASE"
    OPTION_EXERCISE = "OPTION_EXERCISE"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="mock_user")
    date = Column(Date, index=True)
    transaction_type = Column(Enum(TransactionType))
    symbol = Column(String, index=True)
    shares = Column(Float)
    price = Column(Float)
    currency = Column(String)
    broker = Column(String)
    reference_id = Column(String, nullable=True)

class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="mock_user")
    date = Column(Date, index=True)
    symbol = Column(String, index=True)
    shares = Column(Float)
    price = Column(Float)
    cost_inr = Column(Float)
    available_shares = Column(Float)
    currency = Column(String)

    @classmethod
    def get_available_lots(cls, db, user_id: str, symbol_name: str):
        return db.query(cls).filter(
            cls.user_id == user_id,
            func.lower(cls.symbol) == symbol_name.lower(),
            cls.available_shares > 0
        ).order_by(cls.date, cls.id).all()

class TaxCalculation(Base):
    __tablename__ = "tax_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="mock_user")
    sell_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    date = Column(Date)
    symbol = Column(String)
    shares = Column(Float)
    cost_inr = Column(Float)
    sale_inr = Column(Float)
    gain_inr = Column(Float)
    holding_type = Column(String) # STCG or LTCG

Index('idx_lot_symbol_lower_user', Lot.user_id, func.lower(Lot.symbol))
