import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import router
from backend.models.database import engine, Base
from sqlalchemy import inspect, text

# Configure OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

# Set up resource for service identification
resource = Resource.create({
    "service.name": os.getenv("OTEL_SERVICE_NAME", "foreign-stock-tax-calculator-api"),
    "service.version": "1.0.0",
})

# Create OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://ingest.kubiks.app"),
    headers={
        "x-kubiks-key": os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""),
    },
)

# Create tracer provider
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

# Instrument libraries
FastAPIInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()
RequestsInstrumentor().instrument()

# Create database tables
Base.metadata.create_all(bind=engine)

# Handle schema migrations for existing databases
def run_migrations():
    inspector = inspect(engine)

    if 'lots' in inspector.get_table_names():
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_lot_symbol_lower_user ON lots (user_id, lower(symbol))"))
                conn.commit()
            logger.info("Functional index 'idx_lot_symbol_lower_user' ensured")
        except Exception:
            logger.error("Error creating functional index")

    if 'lots' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('lots')]
        if 'currency' not in columns:
            logger.info("Adding 'currency' column to 'lots' table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE lots ADD COLUMN currency VARCHAR"))
                conn.commit()
            logger.info("Column 'currency' added successfully")

    if 'transactions' in inspector.get_table_names():
        if engine.dialect.name == 'postgresql':
            with engine.execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
                try:
                    conn.execute(text("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'OPTION_EXERCISE'"))
                except Exception:
                    logger.error("Enum modification error")
                    raise
        elif engine.dialect.name == 'sqlite':
            with engine.connect() as conn:
                try:
                    # Attempt to recreate the CHECK constraint for SQLite if possible
                    # SQLite does NOT support DROP CONSTRAINT or ADD CONSTRAINT.
                    # We will issue a raw query as suggested by the prompt, even if it might fail.
                    conn.execute(text("ALTER TABLE transactions ADD CONSTRAINT transactiontype_check CHECK (transaction_type IN ('BUY', 'SELL', 'RSU_VEST', 'ESPP_PURCHASE', 'OPTION_EXERCISE'))"))
                    conn.commit()
                except Exception:
                    # We expect this to fail on standard SQLite, but we catch it.
                    conn.rollback()


run_migrations()

app = FastAPI(title="Foreign Stock Tax Calculator API")

# Configure CORS for frontend
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Foreign Stock Tax Calculator API"}
