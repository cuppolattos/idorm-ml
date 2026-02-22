import requests
import json

regions = ["jakarta_utara", "jakarta_pusat", "jakarta_selatan", "yogyakarta"]

sample = {
    "luas_kamar": 12.0,
    "tipe_kos": "putra",
    "is_km_dalam": 1,
    "is_water_heater": 1,
    "is_furnished": 1,
    "is_listrik_free": 0,
    "is_parkir_mobil": 1,
    "is_mesin_cuci": 0,
    "jarak_ke_bca": 1.5
}

print("Testing API Endpoints...\n")

for region in regions:
    url = f"http://localhost:8000/predict/{region}"
    try:
        response = requests.post(url, json=sample)
        if response.status_code == 200:
            pred = response.json().get("predicted_price", 0)
            print(f"{region}: Rp {pred:,.0f} (Status: {response.status_code})")
        else:
            print(f"{region}: Error {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to API for {region}. Is the server running?")

