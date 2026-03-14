from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from backend.models.database import get_db
from backend.models.schema import Transaction, Lot, TaxCalculation
from backend.parsers.shareworks_parser import parse_shareworks
from backend.parsers.fidelity_parser import parse_fidelity
from backend.parsers.generic_parser import infer_schema_with_ai, parse_generic_with_mapping
from backend.services.tax_engine import process_transactions
from pydantic import BaseModel
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

MOCK_USER_ID = "mock_user"

class MappingConfirmation(BaseModel):
    mapping: dict

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), broker: str = "generic", db: Session = Depends(get_db)):
    """
    Uploads a broker statement, parses transactions, and stores them.
    If broker is generic, it infers the mapping using AI and returns it for confirmation.
    """
    content = await file.read()
    filename = file.filename

    try:
        filename_lower = filename.strip().lower()
        if filename_lower.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(content))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid CSV format") from None
        elif filename_lower.endswith('.xlsx') or filename_lower.endswith('.xls'):
            try:
                df = pd.read_excel(io.BytesIO(content))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid Excel format")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if broker == "shareworks":
            transactions_data = parse_shareworks(df)
        elif broker == "fidelity":
            transactions_data = parse_fidelity(df)
        elif broker == "generic":
            header = list(df.columns)
            sample = df.head(20).to_dict(orient="records")
            inferred_mapping = infer_schema_with_ai(header, sample)

            import uuid
            import os
            _, ext = os.path.splitext(filename_lower)
            temp_filename = str(uuid.uuid4()) + ext

            # Save the file content temporarily for later confirmation
            with open(f"/tmp/{temp_filename}", "wb") as f:
                f.write(content)

            return {
                "status": "requires_mapping",
                "message": "Please confirm the inferred column mapping.",
                "inferred_mapping": inferred_mapping,
                "filename": temp_filename
            }
        else:
            raise HTTPException(status_code=400, detail="Unknown broker")

        # Clear existing transactions for idempotency
        db.query(Transaction).filter(Transaction.user_id == MOCK_USER_ID).delete()

        for tx in transactions_data:
            db_tx = Transaction(**tx, user_id=MOCK_USER_ID)
            db.add(db_tx)

        db.commit()

        # Process transactions into lots and calculate taxes
        process_transactions(db, MOCK_USER_ID)

        return {"status": "success", "message": f"Processed {len(transactions_data)} transactions"}

    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve)) from None
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/confirm-mapping/{filename}")
async def confirm_mapping(filename: str, confirmation: MappingConfirmation, db: Session = Depends(get_db)):
    """
    Confirm mapping for generic file upload and process transactions.
    """
    try:
        import os
        import uuid

        # Sanitize filename to strictly be a UUID to prevent path traversal
        try:
            base_name, ext = os.path.splitext(filename)
            valid_uuid = uuid.UUID(base_name)
            safe_filename = str(valid_uuid) + ext
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid filename format")

        filepath = os.path.join("/tmp", safe_filename)

        # Security: filename is now a UUID, so we can't trust its extension
        # If we need to support excel, we should probably save the extension or try both
        # Here we just try reading as CSV, and if it fails, try Excel.
        df = None
        try:
            df = pd.read_csv(filepath)
        except Exception:
            try:
                df = pd.read_excel(filepath)
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported file format")

        if df is None:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        transactions_data = parse_generic_with_mapping(df, confirmation.mapping)

        try:
            os.remove(filepath)
        except Exception:
            pass

        # Clear existing transactions for idempotency
        db.query(Transaction).filter(Transaction.user_id == MOCK_USER_ID).delete()

        for tx in transactions_data:
            db_tx = Transaction(**tx, user_id=MOCK_USER_ID)
            db.add(db_tx)

        db.commit()

        # Process transactions into lots and calculate taxes
        process_transactions(db, MOCK_USER_ID)

        return {"status": "success", "message": f"Processed {len(transactions_data)} transactions"}

    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve)) from None
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == MOCK_USER_ID).all()

@router.get("/results")
def get_results(db: Session = Depends(get_db)):
    """
    Returns the capital gains results.
    """
    results = db.query(TaxCalculation).filter(TaxCalculation.user_id == MOCK_USER_ID).order_by(TaxCalculation.date).all()
    return results

from backend.services.portfolio_service import get_portfolio
from backend.services.trade_simulator import simulate_trade
from datetime import date
from typing import Dict, Optional

class SimulateTradeRequest(BaseModel):
    symbol: str
    shares: float
    price: float
    currency: str
    date: date

@router.get("/portfolio")
def api_get_portfolio(manual_prices: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns portfolio holdings and summary statistics.
    manual_prices can be passed as a JSON string mapping symbols to prices.
    """
    prices_dict = {}
    if manual_prices:
        import json
        try:
            prices_dict = json.loads(manual_prices)
        except Exception:
            pass

    return get_portfolio(db, MOCK_USER_ID, prices_dict)

@router.post("/simulate-trade")
def api_simulate_trade(request: SimulateTradeRequest, db: Session = Depends(get_db)):
    """
    Simulates a trade and returns tax estimations.
    """
    try:
        return simulate_trade(
            db=db,
            user_id=MOCK_USER_ID,
            symbol=request.symbol,
            shares=request.shares,
            price=request.price,
            currency=request.currency,
            sale_date=request.date
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        print(f"Error simulating trade: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/holdings")
def api_get_holdings(db: Session = Depends(get_db)):
    """
    Returns only the portfolio holdings.
    """
    portfolio = get_portfolio(db, MOCK_USER_ID, {})
    return portfolio["holdings"]

@router.get("/capital-gains")
def api_get_capital_gains(db: Session = Depends(get_db)):
    """
    Alias for /results to return the capital gains results.
    """
    return get_results(db)
