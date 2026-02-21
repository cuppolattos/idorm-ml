# idorm-ml Laravel Integration Guide

This guide is designed for the hybrid-cloud setup connecting Laravel (Azure) to FastAPI (Hugging Face / Internal Server). It outlines how to consume the model inference safely across different regions regardless of their exact feature requirements.

## Universal JSON Payload

A common issue in deploying regional Machine Learning models is dealing with "Feature Mismatches." For example, the model for Jakarta Selatan might require the distances to UGM and ITB, whereas Jakarta Pusat might not.

Our FastAPI endpoint is now **Backend-Agnostic**.
Laravel should **send everything it knows about a Kos**. The API will automatically unpack and filter out unnecessary features without blocking the request. It safely zeroes any missing required features as defaults.

### Endpoint
**`POST {FASTAPI_URL}/predict/{region}`**
Available regions: `jakarta_pusat`, `jakarta_selatan`, `jakarta_utara`, `yogyakarta`.

### Example Request Body (Send Everything!)
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

### Laravel Implementation Pattern

In Laravel, gather all the data regardless of what region is being requested:
```php
$payload = [
    'luas_kamar' => $kos->room_size,
    'jarak_ke_bca' => $kos->bca_distance ?? 0.0,
    // Add all other attributes natively...
    'tipe_kos' => $kos->type, // putra, putri, or campur
    'is_km_dalam' => $kos->has_internal_bathroom ? 1 : 0,
    // ...
];

$response = Http::post(env('FASTAPI_MODEL_URL') . "/predict/{$kos->region}", $payload);

$predictedPrice = $response->json('predicted_price');
```

## MLflow Training Template

The local physical versions map (`models/`) has been removed in favor of native MLflow operations.

To train a new model or region:
1. Run your regular Scikit-Learn training pipelines in Jupyter Notebook.
2. Ensure you import the updated `train_and_log_model` from `mlflow_training/utils.py`.
3. Use the updated cell function replacing `joblib.dump`:

```python
from utils import train_and_log_model

# Let MLflow calculate the required columns dynamically based on your trained DataFrame
# and register the model straight to the "production" alias in the local registry
model_uri = train_and_log_model(
    region="jakarta_pusat",
    model=final_model,
    X_train=X_train,
    y_pred=y_pred,
    metrics={"MAE": final_mae, "R2": final_r2, "RMSE": final_rmse, "MAPE": final_mape}
)

print(f"Model saved to registry successfully at: {model_uri}")
```

Your FastAPI app will dynamically load whatever is tagged `@production` for that region in the registry without requiring a rebuild!
