from prometheus_client import Counter, Histogram, Gauge

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
