import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import router
from backend.models.database import engine, Base

# Configure OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# Set up resource for service identification
resource = Resource.create({
    "service.name": os.getenv("OTEL_SERVICE_NAME", "foreign-stock-tax-calculator-api"),
    "service.version": "1.0.0",
})

# Create OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://ingest.kubiks.app"),
)

# Create tracer provider
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Foreign Stock Tax Calculator API")

# Instrument libraries
FastAPIInstrumentor().instrument(app=app)
SQLAlchemyInstrumentor().instrument(engine=engine)
RequestsInstrumentor().instrument()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Foreign Stock Tax Calculator API"}
