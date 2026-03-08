<<<<<<< HEAD
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.transaction import Transaction, TaxResult
from backend.parsers import shareworks_parser, fidelity_parser, generic_parser
from backend.services.tax_engine import calculate_gains
import os
import shutil
import tempfile

app = FastAPI(title="Foreign Stock Tax Calculator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router
from models.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Foreign Stock Tax Calculator API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
>>>>>>> origin/main
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Foreign Stock Tax Calculator API"}

@app.post("/upload")
async def upload_file(broker: str, file: UploadFile = File(...)):
    # Save uploaded file to temporary path
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        transactions = []
        if broker.lower() == 'shareworks':
            transactions = shareworks_parser.parse(tmp_path)
        elif broker.lower() == 'fidelity':
            transactions = fidelity_parser.parse(tmp_path)
        else:
            # Fallback to generic AI parser
            transactions = generic_parser.parse(tmp_path)

        return [t.model_dump() for t in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/calculate", response_model=list[TaxResult])
def calculate_tax(transactions: list[Transaction]):
    return calculate_gains(transactions)
=======
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Foreign Stock Tax Calculator API"}
>>>>>>> origin/main
