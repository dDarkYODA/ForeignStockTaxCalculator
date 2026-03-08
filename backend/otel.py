"""
OpenTelemetry instrumentation for FastAPI backend
"""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentation
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentation
from opentelemetry.instrumentation.requests import RequestsInstrumentation

def setup_otel():
    """Initialize OpenTelemetry tracing"""
    
    # Get configuration from environment variables
    otlp_endpoint = os.getenv(
        'OTEL_EXPORTER_OTLP_ENDPOINT',
        'https://ingest.kubiks.app'
    )
    otlp_headers = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'foreign-stock-tax-calculator-backend')
    
    # Create resource
    resource = Resource.create({
        SERVICE_NAME: service_name,
        'environment': os.getenv('ENVIRONMENT', 'development'),
    })
    
    # Create OTLP exporter
    headers = {}
    if otlp_headers:
        # Parse headers (format: "key=value,key2=value2" or just "api-key")
        if '=' in otlp_headers:
            for header in otlp_headers.split(','):
                if '=' in header:
                    k, v = header.split('=', 1)
                    headers[k.strip()] = v.strip()
        else:
            headers['x-kubiks-key'] = otlp_headers
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        headers=headers,
    )
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument FastAPI and HTTP libraries
    FastAPIInstrumentation().instrument()
    HTTPXClientInstrumentation().instrument()
    RequestsInstrumentation().instrument()
    
    print(f"OpenTelemetry initialized for {service_name}")
    return tracer_provider

# Get tracer instance
tracer = trace.get_tracer(__name__)
