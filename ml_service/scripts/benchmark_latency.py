import time
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

N_RUNS = 2000

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATHS = {
    "jakarta_pusat": MODEL_DIR / "jakarta_pusat_model.pkl",
    "jakarta_selatan": MODEL_DIR / "jakarta_selatan_model.pkl",
    "jakarta_utara": MODEL_DIR / "jakarta_utara_model.pkl",
    "yogyakarta": MODEL_DIR / "yogyakarta_model.pkl",
}

def generate_sample(region):
    base = {
        "luas_kamar": 12,
        "tipe_kos": "campur",
        "is_km_dalam": 1,
        "is_water_heater": 1,
        "is_furnished": 1,
        "is_listrik_free": 0,
        "is_parkir_mobil": 1,
        "is_mesin_cuci": 0,
    }

    if region in ["jakarta_pusat", "yogyakarta"]:
        base["jarak_ke_bca"] = 1.5

    # always compute amenities (safe even if not used)
    base["amenities_count"] = (
        base["is_furnished"]
        + base["is_water_heater"]
        + base["is_km_dalam"]
        + base["is_listrik_free"]
        + base["is_mesin_cuci"]
        + base["is_parkir_mobil"]
    )

    return pd.DataFrame([base])


def benchmark_model(region, model_path):

    print(f"\nBenchmarking {region}")

    model = joblib.load(model_path)
    sample = generate_sample(region)

    latencies = []

    for _ in range(50):
        model.predict(sample)

    for _ in range(N_RUNS):
        start = time.perf_counter()
        model.predict(sample)
        end = time.perf_counter()

        latencies.append((end - start) * 1000)  # ms

    latencies = np.array(latencies)

    print(f"Runs: {N_RUNS}")
    print(f"P50 : {np.percentile(latencies, 50):.4f} ms")
    print(f"P90 : {np.percentile(latencies, 90):.4f} ms")
    print(f"P95 : {np.percentile(latencies, 95):.4f} ms")
    print(f"Mean: {latencies.mean():.4f} ms")
    print(f"Std : {latencies.std():.4f} ms")
    print(f"Min : {latencies.min():.4f} ms")
    print(f"Max : {latencies.max():.4f} ms")


if __name__ == "__main__":
    for region, path in MODEL_PATHS.items():
        benchmark_model(region, path)
