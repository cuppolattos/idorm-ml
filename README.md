# 🏠 Kos Price Prediction API

# 📌 Overview

Kos Price Prediction API adalah sistem Machine Learning yang digunakan untuk memprediksi harga kos berdasarkan fitur properti dan fasilitas, dengan dukungan multi-region:
1. Jakarta Pusat
2. Jakarta Selatan
3. Jakarta Utara
4. Yogyakarta

API ini dirancang dengan pendekatan Enterprise ML Engineering, mencakup:
1. Model Versioning
2. Structured Logging (JSON-based)
3. Latency Monitoring (P50, P90, P95)
4. Prediction Monitoring
5. Anomaly Detection
6. Prometheus Metrics Integration
7. Request ID Tracking
8. Global Exception Handling
9. Rolling Memory Control
10. Production-Ready Architecture

# 🧠 Machine Learning Methodology
1️⃣ Data Processing

* Outlier handling menggunakan 99th percentile capping
* Multicollinearity mitigation

Feature engineering:
amenities_count (tree-based models only)

Feature separation:
Linear models: interpretable design
Tree models: enhanced non-linear capability

2️⃣ Model Selection Strategy

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

# 🏗️ System Architecture
Frontend (Laravel)
        ↓
FastAPI Inference Service
        ↓
Region-based Model Loader
        ↓
Scikit-learn Pipeline
        ↓
Prediction Output
        ↓
Logging + Metrics + Monitoring
        ↓
Prometheus
        ↓
Grafana Dashboard

# 📂 Project Structure
app/
│
├── main.py
├── router.py
├── model_loader.py
├── schema.py
├── middleware.py
├── metrics.py
├── prometheus_metrics.py
├── logging_config.py
│
models/
│   ├── jakarta_pusat/
│   │   └── v1/
│   │       ├── model.pkl
│   │       └── metadata.json
│   ├── jakarta_selatan/
│   ├── jakarta_utara/
│   └── yogyakarta/
│
logs/
│   ├── inference.log
│   └── error.log

# 🔐 Model Versioning

Each region follows:
models/{region}/v{n}/

Example:
models/jakarta_utara/v1/model.pkl

At startup:
1. Latest version automatically loaded
2. Metadata automatically attached
3. Version exposed via /model-info/{region}

# 📊 Observability & Monitoring
1️⃣ Structured Logging

All inference logs are JSON formatted:

{
  "event": "inference_event",
  "region": "jakarta_utara",
  "model_version": "v1",
  "latency_ms": 14.68,
  "predicted_price": 2362990,
  "request_id": "uuid"
}

Stored in:
* logs/inference.log
* logs/error.log

2️⃣ Request ID Tracking

Each request:
* Auto-generate UUID if not provided
* Accept custom X-Request-ID
* Propagated to response header
* Logged in structured format

Enables:
* Distributed tracing
* Production debugging
* Correlation across services

3️⃣ Latency Monitoring

Tracked:
* Mean
* P50
* P90
* P95
* Max

Exposed via:
GET /metrics

4️⃣ Prediction Monitoring

Rolling window (max 1000 samples per region):
1. Mean prediction
2. Percentiles

Endpoint:
GET /prediction-monitor/{region}

5️⃣ Anomaly Detection

Two layers:
1. Hard Threshold
Prediction outside defined price range.
2. Statistical (IQR-based)
Dynamic outlier detection after minimum 20 samples.

Endpoint:
GET /anomaly-monitor/{region}

6️⃣ Prometheus Metrics

Integrated metrics:
* prediction_requests_total
* prediction_errors_total
* prediction_request_latency_seconds
* prediction_latest_prediction

Exposed at:
GET /prometheus-metrics

7️⃣ Grafana Dashboard Ready

Recommended panels:
* Total Requests
* Request Rate
* Error Rate
* P95 Latency
* Latest Prediction
* Per-region traffic

# 🚦 Available Endpoints
1. Prediction
POST /predict/{region}

2. Health Check
GET /health

3. Model Info
GET /model-info/{region}

4. Metrics Summary
GET /internal-metrics

5. Prediction Monitoring
GET /prediction-monitor/{region}

6. Anomaly Monitoring
GET /anomaly-monitor/{region}

7. Prometheus Metrics
GET /metrics

# 🛡️ Production Safeguards

* Global exception handler
* No raw stack trace exposure
* Request ID tracking
* Rolling memory limit (1000 records)
* Structured JSON logs
* Version-aware model loading
* Metadata-based configuration

# 📦 Deployment Notes
Local Development

Run API:
uvicorn app.main:app --port 8001 --reload

Laravel backend may run on:
localhost:8000

Inference service recommended on:
localhost:8001

Prometheus:
localhost:9090

Grafana Monitoring:
localhost:3000

# 📈 Performance Benchmarks

Measured over 2000 runs:

Region	P50 (ms)	P95 (ms)
Jakarta Pusat	~31 ms	~34 ms
Jakarta Selatan	~15 ms	~24 ms
Jakarta Utara	~1.7 ms	~2.1 ms
Yogyakarta	~31 ms	~32 ms

System latency stable within acceptable production range.

# 🧪 Model Governance

Each model version includes:
metadata.json

Example:

{
  "model_name": "Linear Regression",
  "version": "v1",
  "region": "jakarta_utara",
  "training_date": "2026-02-15",
  "r2_test": 0.6627,
  "mae_test": 348762,
  "notes": "Selected for stability and interpretability"
}

# 🏁 Enterprise Maturity Level

This system implements:
1. MLOps Monitoring
2. Observability
3. Version Control
4. Drift Detection
5. Structured Logging
6. Performance Benchmarking
7. Deployment Separation
8. Production Safety Guards

# 👥 Backend Integration Notes

Laravel Backend Responsibilities:
1. Calculate jarak_ke_bca (Haversine)
2. Send structured JSON request
3. Handle response and display prediction

Optional: pass custom X-Request-ID

1. ML Service Responsibilities:
2. Validate input
3. Load correct model
4. Predict
5. Monitor
6. Log
7. Expose metrics

# 📌 Final Notes

This project demonstrates:
1. Applied Machine Learning
2. Production Engineering
3. Monitoring and Observability
4. Enterprise Software Practices
5. Clean API Architecture

If needed, next improvements can include:
* Docker containerization
* CI/CD pipeline
* Model A/B testing
* Drift detection dashboard
* Alerting system
* Centralized log aggregation