import braintrust
import os

_logger_initialized = False

def init_braintrust():
    global _logger_initialized
    if not _logger_initialized:
        braintrust.init_logger(project="ForeignStockTaxCalculator")
        _logger_initialized = True

def log_ai_call(input_sample, prompt, response, metadata=None):
    if metadata is None:
        metadata = {}

    init_braintrust()
    with braintrust.traced(
        name="ai_schema_inference",
        metadata=metadata
    ) as span:
        span.log(
            inputs={"input_sample": input_sample, "prompt": prompt},
            output=response
        )
