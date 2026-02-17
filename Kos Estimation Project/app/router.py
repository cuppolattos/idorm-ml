from fastapi import APIRouter, HTTPException, Request
from app.schema import KosRequest, PredictionResponse
from app.model_loader import model_loader
import pandas as pd
import time
import logging
import json

from collections import defaultdict, deque
import statistics

from app.metrics import metrics_tracker

from app.prometheus_metrics import (
    REQUEST_COUNT,
    ERROR_COUNT,
    REQUEST_LATENCY,
    LATEST_PREDICTION
)

prediction_store = defaultdict(lambda: deque(maxlen=1000))
anomaly_store = defaultdict(lambda: deque(maxlen=1000))
latency_store = defaultdict(lambda: deque(maxlen=1000))

error_counter = 0
logger = logging.getLogger("inference")

router = APIRouter()

@router.post("/predict/{region}", response_model=PredictionResponse)
def predict(region: str, request: KosRequest, http_request: Request):
    global error_counter

    model_info = model_loader.get_model(region)

    if model_info is None:
        raise HTTPException(status_code=404, detail="Region not found")

    model = model_info["model"]
    version = model_info["version"]

    request_id = http_request.state.request_id

    # prometheus, increment request counter
    REQUEST_COUNT.labels(region=region).inc()

    try:
        with REQUEST_LATENCY.labels(region=region).time():

            data = request.dict()

            data["amenities_count"] = (
                data["is_furnished"]
                + data["is_water_heater"]
                + data["is_km_dalam"]
                + data["is_listrik_free"]
                + data["is_mesin_cuci"]
                + data["is_parkir_mobil"]
            )

            df = pd.DataFrame([data])
            prediction = model.predict(df)[0]

            # store rolling prediction
            prediction_store[region].append(float(prediction))

            LATEST_PREDICTION.labels(region=region).set(float(prediction))

        # logging
        logger.info(
            "inference_event",
            extra={
                "region": region,
                "model_version": version,
                "request_id": request_id,
                "predicted_price": round(float(prediction), 2)
            }
        )

        return PredictionResponse(
            region=region,
            predicted_price=round(float(prediction), 2),
            model_version=version
        )

    except Exception as e:
        error_counter += 1

        # prometheus error counter
        ERROR_COUNT.labels(region=region).inc()

        logger.error(
            "inference_error",
            extra={
                "region": region,
                "error": str(e),
                "request_id": request_id
            }
        )

        raise HTTPException(status_code=500, detail="Prediction failed")
    

@router.get("/anomaly-monitor/{region}")
def anomaly_monitor(region: str):

    anomalies = anomaly_store.get(region, [])

    return {
        "region": region,
        "total_anomalies": len(anomalies),
        "details": anomalies[-10:]
    }

@router.get("/model-info/{region}")
def model_info(region: str):
    info = model_loader.get_model_info(region)

    if info is None:
        raise HTTPException(status_code=404, detail="Region not found")

    return {
        "region": region,
        "version": info["version"],
        "metadata": info["metadata"]
    }

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": list(model_loader.models.keys())
    }

@router.get("/internal-metrics")
def internal_metrics():
    result = {}

    for region, latencies in latency_store.items():
        if not latencies:
            continue

        sorted_lat = sorted(latencies)

        result[region] = {
            "count": len(latencies),
            "mean_ms": round(statistics.mean(latencies), 4),
            "p50_ms": round(sorted_lat[int(0.50 * len(sorted_lat))], 4),
            "p90_ms": round(sorted_lat[int(0.90 * len(sorted_lat))], 4),
            "p95_ms": round(sorted_lat[int(0.95 * len(sorted_lat))], 4),
            "max_ms": round(max(latencies), 4),
        }

    return {
        "regions": result,
        "total_errors": error_counter
    }

@router.get("/prediction-monitor/{region}")
def prediction_monitor(region: str):

    preds = prediction_store.get(region, [])

    if not preds:
        return {"message": "No predictions yet"}

    sorted_preds = sorted(preds)

    return {
        "region": region,
        "count": len(preds),
        "mean_prediction": round(statistics.mean(preds), 2),
        "p50": round(sorted_preds[int(0.50 * len(sorted_preds))], 2),
        "p90": round(sorted_preds[int(0.90 * len(sorted_preds))], 2),
        "p95": round(sorted_preds[int(0.95 * len(sorted_preds))], 2),
        "max_prediction": round(max(preds), 2),
        "min_prediction": round(min(preds), 2),
    }