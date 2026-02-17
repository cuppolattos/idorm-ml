import joblib
import pandas as pd

models = {
    "jakut": joblib.load("models/jakarta_utara_model.pkl"),
    "jakpus": joblib.load("models/jakarta_pusat_model.pkl"),
    "jaksel": joblib.load("models/jakarta_selatan_model.pkl"),
    "jogja": joblib.load("models/yogyakarta_model.pkl")
}

sample = pd.DataFrame([{
    "luas_kamar": 12,
    "tipe_kos": "putra",
    "is_km_dalam": 1,
    "is_water_heater": 1,
    "is_furnished": 1,
    "is_listrik_free": 0,
    "is_parkir_mobil": 1,
    "is_mesin_cuci": 0,
}])

for region, model in models.items():
    pred = model.predict(sample)[0]
    print(f"{region}: Rp {pred:,.0f}")

