# 🏠 Kos Price Prediction API

> **MLOps-powered REST API** for predicting boarding house (kos) rental prices across Indonesian regions, with full model lifecycle management, observability, and production governance.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [MLflow Model Lifecycle](#mlflow-model-lifecycle)
- [Observability Stack](#observability-stack)
- [Training Pipeline](#training-pipeline)
- [Semantic Versioning](#semantic-versioning)
- [Production Governance](#production-governance)

---

## Overview

This system predicts fair monthly rental prices for **kos** (Indonesian boarding houses) based on room attributes such as size, amenities, location proximity, and kos type. It supports **4 regional models**:

| Region | Description |
|--------|-------------|
| `jakarta_pusat` | Central Jakarta |
| `jakarta_selatan` | South Jakarta |
| `jakarta_utara` | North Jakarta |
| `yogyakarta` | Yogyakarta |

Each region has its own independently trained and versioned ML model, served through a unified FastAPI endpoint.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Laravel / Postman)            │
│                POST /predict/{region}                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│  ┌──────────┐  ┌────────────┐  ┌─────────────────────┐  │
│  │  Router  │→ │  Schema    │→ │  Smart Feature      │  │
│  │ /predict │  │ Validation │  │  Alignment Engine   │  │
│  └──────────┘  └────────────┘  └──────────┬──────────┘  │
│                                           │              │
│  ┌────────────────────────────────────────▼───────────┐  │
│  │          ModelProvider (Singleton)                  │  │
│  │  jakarta_pusat  │ jakarta_selatan │ jakarta_utara  │  │
│  │                 │   yogyakarta    │                │  │
│  └────────────────────────┬──────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────▼──────────────────────────┐  │
│  │  Prometheus Metrics  │  Structured JSON Logging   │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
          ┌────────────┴──────────────┐
          ▼                           ▼
┌──────────────────┐      ┌────────────────────┐
│  MLflow Registry │      │  Docker Compose     │
│  notebooks/      │      │  ┌──────────────┐   │
│  ├── mlflow.db   │      │  │  Prometheus  │   │
│  └── mlruns/     │      │  │  :9090       │   │
│                  │      │  └──────┬───────┘   │
│  @production     │      │  ┌──────▼───────┐   │
│  alias per model │      │  │   Grafana    │   │
└──────────────────┘      │  │   :3001      │   │
                          │  └──────────────┘   │
                          └────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI + Uvicorn |
| **ML Models** | Scikit-learn (RandomForest, GradientBoosting, Ridge) |
| **Model Registry** | MLflow (SQLite backend) |
| **Validation** | Pydantic v2 |
| **Monitoring** | Prometheus + Grafana (Docker) |
| **Logging** | Structured JSON (python-json-logger) |
| **Data Processing** | Pandas, NumPy |

---

## Project Structure

```
Kos Estimation Project/
├── app/                          # FastAPI application
│   ├── main.py                   # App entrypoint, exception handlers
│   ├── router.py                 # Prediction & monitoring endpoints
│   ├── schema.py                 # Pydantic request/response models
│   ├── model_loader.py           # MLflow model loading (singleton)
│   ├── metrics.py                # Prometheus metric definitions
│   ├── middleware.py              # Request ID & latency middleware
│   ├── logging_config.py         # JSON logging setup
│   └── prometheus_metrics.py     # Additional Prometheus metrics
│
├── notebooks/                    # Training notebooks & MLflow data
│   ├── jakarta_pusat.ipynb       # Training notebook - Jakarta Pusat
│   ├── jakarta_selatan.ipynb     # Training notebook - Jakarta Selatan
│   ├── jakarta_utara.ipynb       # Training notebook - Jakarta Utara
│   ├── yogyakarta.ipynb          # Training notebook - Yogyakarta
│   ├── mlflow.db                 # MLflow tracking database
│   └── mlruns/                   # MLflow model artifacts
│
├── datasets/                     # Raw CSV datasets per region
│   ├── jakarta_pusat.csv
│   ├── jakarta_selatan.csv
│   ├── jakarta_utara.csv
│   └── yogyakarta.csv
│
├── src/training/
│   └── utils.py                  # MLflow train & register utility
│
├── scripts/                      # Helper & test scripts
│   ├── retrain_all.py            # Retrain all models (CLI)
│   ├── test_model.py             # API prediction test
│   └── test_all_endpoints.py     # Full endpoint verification
│
├── docs/                         # Documentation
│   ├── integration_guide.md      # Laravel integration guide
│   └── production_governance.md  # Governance framework
│
├── logs/                         # Runtime logs
│   ├── inference.log             # Inference event logs
│   └── error.log                 # Error logs
│
├── docker-compose.yml            # Prometheus + Grafana
├── prometheus.yml                # Prometheus scrape config
└── requirements.txt              # Python dependencies
```

---

## Getting Started

### Prerequisites

- **Python** 3.10+
- **Docker Desktop** (for monitoring stack)
- **pip** package manager

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install watchfiles   # Required for --reload to work properly
```

### 2. Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

> **Important:** The `watchfiles` package must be installed for `--reload` to work correctly. Without it, the file watcher monitors all files (including logs and DB) causing restart loops.

### 3. Start Monitoring Stack (Optional)

```bash
docker compose up -d
```

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | — |
| **Prometheus** | http://localhost:9090 | — |
| **Grafana** | http://localhost:3001 | admin / admin |

### 4. Verify Installation

```bash
python scripts/test_model.py
```

Expected output:
```
Testing API Endpoints...

jakarta_utara: Rp 2,374,581 (Status: 200)
jakarta_pusat: Rp 2,920,512 (Status: 200)
jakarta_selatan: Rp 2,909,030 (Status: 200)
yogyakarta: Rp 1,813,426 (Status: 200)
```

---

## API Documentation

### `POST /predict/{region}`

Predict kos rental price for a given region.

**Request Body:**
```json
{
  "luas_kamar": 15.0,
  "jarak_ke_bca": 2.5,
  "tipe_kos": "campur",
  "is_km_dalam": 1,
  "is_water_heater": 0,
  "is_furnished": 1,
  "is_listrik_free": 0,
  "is_parkir_mobil": 1,
  "is_mesin_cuci": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `luas_kamar` | float | Room size in m² (0–100) |
| `jarak_ke_bca` | float | Distance to nearest BCA in km (0–50) |
| `tipe_kos` | string | `putra`, `putri`, or `campur` |
| `is_km_dalam` | 0/1 | Has private bathroom |
| `is_water_heater` | 0/1 | Has water heater |
| `is_furnished` | 0/1 | Is furnished |
| `is_listrik_free` | 0/1 | Free electricity |
| `is_parkir_mobil` | 0/1 | Has car parking |
| `is_mesin_cuci` | 0/1 | Has washing machine |

**Response:**
```json
{
  "region": "jakarta_pusat",
  "predicted_price": 2920511.76,
  "model_version": "v1.0.0"
}
```

### `GET /health`

Health check with loaded model status.

```json
{
  "status": "healthy",
  "models_loaded": ["jakarta_pusat", "jakarta_selatan", "jakarta_utara", "yogyakarta"]
}
```

### `GET /model-info/{region}`

Returns model version, metadata, and signature.

### `GET /prediction-monitor/{region}`

Rolling prediction statistics (mean, p50, p90, p95, min, max).

### `GET /anomaly-monitor/{region}`

Anomaly detection results.

### `GET /internal-metrics`

Internal latency percentiles and error counts.

### `GET /metrics`

Prometheus-compatible metrics endpoint (auto-instrumented).

---

## MLflow Model Lifecycle

Models are managed through **MLflow Model Registry** with a local SQLite backend.

### How It Works

1. **Training** → Jupyter notebooks in `notebooks/` train regional models
2. **Registration** → `train_and_register()` logs the model to MLflow with signature & metrics
3. **Alias** → The `@production` alias is automatically set on the new version
4. **Serving** → FastAPI loads whatever version has the `@production` alias

### Model Registry Commands

```python
# Check registered models
from mlflow.tracking import MlflowClient
client = MlflowClient()
print([m.name for m in client.search_registered_models()])

# Check production alias
client.get_model_version_by_alias("jakarta_pusat_model", "production")
```

### Retrain All Models

```bash
python scripts/retrain_all.py
```

This retrains all 4 regional models with the current scikit-learn version and re-registers them in MLflow.

---

## Observability Stack

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `prediction_requests_total` | Counter | Total requests per region |
| `prediction_errors_total` | Counter | Total errors per region |
| `prediction_latency_seconds` | Histogram | Request latency per region |
| `latest_prediction_value` | Gauge | Most recent prediction |
| `model_load_status` | Gauge | Model load status (1=ok, 0=fail) |
| `prediction_value_summary` | Summary | Prediction distribution for drift detection |

### Grafana Setup

1. Open Grafana at http://localhost:3001
2. Add data source → **Prometheus** → URL: `http://prometheus:9090`
3. Create dashboards using the metrics above

### Structured Logging

All logs are JSON-formatted with request tracing:
```json
{
  "asctime": "2026-02-22 00:14:20",
  "levelname": "INFO",
  "name": "inference",
  "message": "inference_event",
  "region": "yogyakarta",
  "model_version": "v1.0.0",
  "request_id": "99f25a6d-...",
  "latency_sec": 0.102
}
```

---

## Training Pipeline

Each notebook follows this standardized pipeline:

```
Raw CSV Data
    │
    ▼
Data Loading & EDA
    │  └── Shape validation, data quality checks
    ▼
Outlier Handling
    │  └── IQR analysis, 99th percentile capping
    ▼
Feature Engineering
    │  ├── amenities_count (sum of 6 binary features)
    │  └── luas_kamar clipping
    ▼
Feature Selection
    │  └── Correlation analysis, drop non-informative features
    ▼
Stratified Train/Test Split
    │  └── Best seed search across 8 candidates
    ▼
Preprocessing (ColumnTransformer)
    │  ├── RobustScaler → continuous features
    │  ├── Passthrough → binary features
    │  └── OneHotEncoder → categorical (tipe_kos)
    ▼
Model Training & Tuning
    │  ├── Random Forest (RandomizedSearchCV)
    │  ├── Gradient Boosting (RandomizedSearchCV)
    │  └── Overfitting guard (gap threshold)
    ▼
Model Selection & Evaluation
    │  └── R², MAE, RMSE, MAPE
    ▼
MLflow Registration
    └── train_and_register() → @production alias
```

### Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `nama_kos` | string | Kos name (dropped before training) |
| `harga` | int | Monthly price in Rupiah (target) |
| `luas_kamar` | float | Room size (m²) |
| `jarak_ke_bca` | float | Distance to BCA (km) |
| `tipe_kos` | string | putra / putri / campur |
| `is_ac` | 0/1 | Has AC (typically dropped — zero variance) |
| `is_km_dalam` | 0/1 | Private bathroom |
| `is_water_heater` | 0/1 | Water heater |
| `is_furnished` | 0/1 | Furnished |
| `is_internet` | 0/1 | Internet (typically dropped — zero variance) |
| `is_listrik_free` | 0/1 | Free electricity |
| `is_parkir_mobil` | 0/1 | Car parking |
| `is_mesin_cuci` | 0/1 | Washing machine |

---

## Semantic Versioning

Models follow **semantic versioning** (`vMAJOR.MINOR.PATCH`):

| Bump | When | Example |
|------|------|---------|
| **MAJOR** | Model architecture change | `v1.0.0 → v2.0.0` |
| **MINOR** | Performance improvement | `v1.0.0 → v1.1.0` |
| **PATCH** | Bug fix / preprocessing tweak | `v1.0.0 → v1.0.1` |

### Usage in Training

```python
from utils import train_and_register

model_uri = train_and_register(
    region="jakarta_pusat",
    model=final_model,
    X_train=X_train, y_train=y_train,
    X_test=X_test, y_test=y_test,
    params={"model_type": "RandomForestRegressor"},
    metrics={"MAE": mae, "R2": r2, "RMSE": rmse, "MAPE": mape},
    bump="minor"  # "major", "minor", or "patch"
)
```

The semantic version is stored as a tag on the MLflow model version and displayed in API responses.

---

## Production Governance

See [`docs/production_governance.md`](docs/production_governance.md) for the full governance framework covering:

- Model ownership & responsibilities
- Version increment rules
- Metadata governance & validation
- Manual promotion strategy
- Monitoring & observability layers
- Rollback strategy
- Retraining policy
- Security considerations

---

## Laravel Integration

See [`docs/integration_guide.md`](docs/integration_guide.md) for connecting this API to a Laravel backend. Key points:

- **Send everything** — the API auto-filters features per model signature
- **Region-agnostic** — same payload structure for all regions
- **Zero config** — no feature mapping needed on Laravel side

```php
$response = Http::post(env('FASTAPI_MODEL_URL') . "/predict/{$kos->region}", [
    'luas_kamar' => $kos->room_size,
    'jarak_ke_bca' => $kos->bca_distance ?? 0.0,
    'tipe_kos' => $kos->type,
    'is_km_dalam' => $kos->has_internal_bathroom ? 1 : 0,
    // ... other fields
]);

$predictedPrice = $response->json('predicted_price');
```

---

## License

This project is developed for academic purposes at Bina Nusantara University.
