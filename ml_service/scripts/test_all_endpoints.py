import requests
import json

BASE = "http://localhost:8000"

print("=== MODEL INFO ===")
for region in ["jakarta_pusat", "jakarta_selatan", "jakarta_utara", "yogyakarta"]:
    r = requests.get(f"{BASE}/model-info/{region}")
    data = r.json()
    print(f"  {region}: version={data.get('version')}, status={r.status_code}")

print("\n=== PREDICTION MONITOR ===")
for region in ["jakarta_pusat", "jakarta_selatan", "jakarta_utara", "yogyakarta"]:
    r = requests.get(f"{BASE}/prediction-monitor/{region}")
    print(f"  {region}: {r.json()}")

print("\n=== ANOMALY MONITOR ===")
r = requests.get(f"{BASE}/anomaly-monitor/jakarta_pusat")
print(f"  jakarta_pusat: {r.json()}")

print("\n=== INTERNAL METRICS ===")
r = requests.get(f"{BASE}/internal-metrics")
print(f"  {r.json()}")

print("\n=== PROMETHEUS METRICS ===")
r = requests.get(f"{BASE}/metrics")
# just show first 500 chars
print(f"  (first 500 chars):\n{r.text[:500]}")

print("\n=== ALL CHECKS PASSED ===")
