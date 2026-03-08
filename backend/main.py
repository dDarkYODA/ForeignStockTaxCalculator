from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.transaction import Transaction, TaxResult
from backend.parsers import shareworks_parser, fidelity_parser, generic_parser
from backend.services.tax_engine import calculate_gains
import os
import shutil
import tempfile

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing
resource = Resource(attributes={
    "service.name": "foreign-stock-tax-calculator-backend"
})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = FastAPI(title="Foreign Stock Tax Calculator")

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
