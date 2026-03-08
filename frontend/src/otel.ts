import { ZoneContextManager } from '@opentelemetry/context-zone';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { Resource } from '@opentelemetry/resources';
import { SEMRESATTRS_SERVICE_NAME } from '@opentelemetry/semantic-conventions';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-web';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';

const serviceName = 'foreign-stock-tax-calculator-frontend';

const resource = Resource.default().merge(
  new Resource({
    [SEMRESATTRS_SERVICE_NAME]: serviceName,
  }),
);

const tracerProvider = new WebTracerProvider({ resource });

// Configure the OTLP exporter
const otlpExporter = new OTLPTraceExporter({
  url: process.env.REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT || 'https://ingest.kubiks.app/v1/traces',
  headers: process.env.REACT_APP_OTEL_EXPORTER_OTLP_HEADERS
    ? {
        'x-kubiks-key': process.env.REACT_APP_OTEL_EXPORTER_OTLP_HEADERS,
      }
    : {},
});

tracerProvider.addSpanProcessor(new BatchSpanProcessor(otlpExporter));
tracerProvider.register({
  contextManager: new ZoneContextManager(),
});

// Register instrumentations
registerInstrumentations({
  instrumentations: [
    new FetchInstrumentation({
      applyCustomAttributesOnSpan(span, request, response) {
        span.setAttribute('http.client', 'fetch');
      },
      requestHook: (span, request) => {
        span.setAttribute('http.request.url', request.url);
      },
      responseHook: (span, response) => {
        span.setAttribute('http.response.status', response.status);
      },
    }),
    new XMLHttpRequestInstrumentation({
      applyCustomAttributesOnSpan(span, request, response) {
        span.setAttribute('http.client', 'xhr');
      },
    }),
  ],
});

export const tracer = tracerProvider.getTracer(serviceName, '1.0.0');
