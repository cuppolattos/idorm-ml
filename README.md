# Kos Price Prediction API

---

## Overview

Kos Price Prediction API is a production-oriented machine learning inference service built using FastAPI.

The system implements:

* Semantic model versioning
* Metadata integrity validation
* Structured JSON logging
* Request ID traceability
* Prometheus monitoring
* Latency histogram tracking
* Prediction distribution monitoring
* Anomaly detection
* Manual model promotion governance
* Rollback strategy

This project follows controlled MLOps practices suitable for production-level deployment in small-to-mid scale environments.

---

# 🧠 Machine Learning Methodology
1️. Data Processing

* Outlier handling using 99th percentile capping
* Multicollinearity mitigation

Feature engineering:
amenities_count (tree-based models only)

Feature separation:
Linear models: interpretable design
Tree models: enhanced non-linear capability

2️. Model Selection Strategy

Evaluated models:
1. Linear Regression
2. Ridge
3. Lasso
4. Random Forest
5. Gradient Boosting

Selection criteria:
* R² performance
* MAE stability
* Train-test gap
* Overfitting control
* Residual diagnostics
* Interpretability (when applicable)

Final models selected per region based on stability + generalization performance.

# Architecture Overview

```
Client (Laravel)
        ↓
FastAPI Inference Layer
        ↓
Model Loader (Versioned)
        ↓
ML Model (scikit-learn Pipeline)
        ↓
Monitoring (Prometheus)
        ↓
Logs (JSON Structured)
```

---

# 📈 Performance Benchmarks

Measured over 2000 runs:

Region	P50 (ms)	P95 (ms)
Jakarta Pusat	~31 ms	~34 ms
Jakarta Selatan	~15 ms	~24 ms
Jakarta Utara	~1.7 ms	~2.1 ms
Yogyakarta	~31 ms	~32 ms

System latency stable within acceptable production range.

# Key Features

## 1. Semantic Model Versioning

Models are stored in:

```
models/{region}/vMAJOR.MINOR.PATCH/
```

Example:

```
models/jakarta_pusat/v1.0.0/
models/jakarta_pusat/v1.1.0/
```

Only the highest semantic version is loaded during startup.

Version format:

```
vMAJOR.MINOR.PATCH
```

---

## 2. Metadata Governance

Each model folder must contain:

```
model.pkl
metadata.json
```

Metadata includes:

* region
* model_version
* model_type
* params
* metrics (MAE, R2, RMSE, MAPE)
* features
* optional mlflow_run_id

Startup validation ensures:

* Folder version matches metadata
* Region consistency
* Model type consistency
* Feature schema consistency
* Valid semantic version format

The API will fail to start if validation fails.

---

## 3. Monitoring & Observability

Prometheus endpoint:

```
GET /metrics
```

Exposed metrics:

* prediction_requests_total
* prediction_errors_total
* prediction_latency_seconds (histogram)
* latest_prediction_value

Latency is stored in seconds.

Example average latency query (ms):

```
(
  rate(prediction_latency_seconds_sum[5m])
/
  rate(prediction_latency_seconds_count[5m])
) * 1000
```

P95 latency:

```
histogram_quantile(
  0.95,
  rate(prediction_latency_seconds_bucket[5m])
) * 1000
```

---

## 4. Prediction Monitoring

Internal endpoint:

```
GET /prediction-monitor/{region}
```

Provides:

* mean prediction
* p50, p90, p95
* min/max prediction
* count

Used for drift awareness.

---

## 5. Anomaly Detection

Endpoint:

```
GET /anomaly-monitor/{region}
```

Detects:

* Hard threshold violations
* IQR-based statistical outliers

Helps detect abnormal prediction behavior.

---

## 6. Structured Logging

Logging format: JSON

Includes:

* region
* model_version
* latency
* request_id
* prediction value

Two log files:

```
logs/inference.log
logs/error.log
```

Global exception handler prevents raw stack trace exposure.

---

## 7. Request ID Tracking

Each request receives:

```
X-Request-ID
```

Used for:

* Traceability
* Log correlation
* Debugging

Middleware injects and propagates request IDs.

---

## 8. Model Rollback Strategy

If a production issue occurs:

1. Identify faulty version
2. Remove or downgrade folder
3. Restart API
4. System automatically loads highest valid version

Rollback is deterministic due to semantic version sorting.

---

## 9. MLflow Compatibility (Optional)

The architecture supports MLflow integration.

Metadata may include:

```
mlflow_run_id
```

Model registry upgrade path is available without refactoring inference layer.

Current implementation uses filesystem versioning for stability and simplicity.

---

# API Endpoints

## Prediction

```
POST /predict/{region}
```

Example:

```
POST /predict/jakarta_pusat
```

Request body:

```json
{
  "luas_kamar": 20,
  "jarak_ke_bca": 2.5,
  "tipe_kos": "putra",
  "is_km_dalam": 1,
  "is_water_heater": 0,
  "is_furnished": 1,
  "is_listrik_free": 0,
  "is_parkir_mobil": 0,
  "is_mesin_cuci": 1
}
```

Response:

```json
{
  "region": "jakarta_pusat",
  "predicted_price": 3026679.96,
  "model_version": "v1.0.0"
}
```

---

## Health Check

```
GET /health
```

---

## Model Info

```
GET /model-info/{region}
```

---

## Internal Metrics (Non-Prometheus)

```
GET /internal-metrics
```

---

## Prometheus Metrics

```
GET /metrics
```

---

# Installation

## 1. Clone Repository

```
git clone <repo_url>
cd project_directory
```

## 2. Install Dependencies

```
pip install -r requirements.txt
```

## 3. Run Server

```
uvicorn app.main:app --reload --port 8001
```

---

# Prometheus Setup (Local)

1. Install Prometheus
2. Configure `prometheus.yml`

Example:

```
scrape_configs:
  - job_name: "kos_api"
    static_configs:
      - targets: ["localhost:8001"]
```

3. Start Prometheus:

```
.\prometheus.exe --config.file=prometheus.yml
```

Access:

```
http://localhost:9090
```

---

# Governance Summary

The system implements:

* Controlled semantic versioning
* Metadata integrity validation
* Manual promotion policy
* Rollback capability
* Observability
* Structured logging
* Monitoring via Prometheus
* Schema validation via Pydantic

This aligns with small-team production-grade MLOps standards.

---

# 👥 Backend Integration Notes

Laravel Backend Responsibilities:
1. Calculate jarak_ke_bca (Haversine)
2. Send structured JSON request
3. Handle response and display prediction

Optional: pass custom X-Request-ID

---

# Future Improvements

* MLflow full model registry integration
* CI/CD retraining workflow
* Alert-based automatic rollback
* Cloud observability integration

---

# Production Notes

* Latency metrics are stored in seconds.
* At least two samples are required for `rate()` queries.
* Model promotion is manual by design.
* Startup validation prevents corrupted deployments.
* No raw exception exposure in production.

---

# License

Internal academic project – Production governance implemented for learning and portfolio purposes.