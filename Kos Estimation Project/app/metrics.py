from prometheus_client import Counter, Histogram, Gauge, Summary

# Prometheus Integrations

# Total request per region
REQUEST_COUNT = Counter(
    "prediction_requests_total",
    "Total prediction requests",
    ["region"]
)

# Error counter
ERROR_COUNT = Counter(
    "prediction_errors_total",
    "Total prediction errors",
    ["region"]
)

# Latency histogram
REQUEST_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction latency",
    ["region"]
)

# Latest prediction gauge
LATEST_PREDICTION = Gauge(
    "latest_prediction_value",
    "Latest prediction value",
    ["region"]
)

# Model load status
MODEL_LOAD_STATUS = Gauge(
    "model_load_status",
    "Status of model loading per region (1=loaded, 0=not loaded)",
    ["region"]
)

# Prediction value summary for drift detection
PREDICTION_VALUE_SUMMARY = Summary(
    "prediction_value_summary",
    "Summary of predicted values (for drift detection)",
    ["region"]
)

