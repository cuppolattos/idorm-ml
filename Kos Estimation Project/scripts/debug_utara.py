import pandas as pd
df = pd.read_csv('datasets/jakarta_utara.csv')
cols_to_drop = [c for c in df.columns if df[c].nunique() <= 1]
df_clean = df.drop(columns=cols_to_drop)
df_final = df_clean.copy()

df_final['amenities_count'] = (
    df_final.get('is_furnished', 0).astype(int) +
    df_final.get('is_water_heater', 0).astype(int) +
    df_final.get('is_km_dalam', 0).astype(int) +
    df_final.get('is_listrik_free', 0).astype(int) +
    df_final.get('is_mesin_cuci', 0).astype(int) +
    df_final.get('is_parkir_mobil', 0).astype(int)
)

X = df_final.drop(columns=['nama_kos', 'harga'])

continuous_cols_linear = ['luas_kamar', 'jarak_ke_bca']
binary_cols = ['is_water_heater', 'is_km_dalam', 'is_listrik_free', 'is_mesin_cuci', 'is_parkir_mobil', 'is_furnished']
categorical_cols = ['tipe_kos']
continuous_cols_tree = continuous_cols_linear + ['amenities_count']

expected_cols = set(continuous_cols_tree + binary_cols + categorical_cols)
actual_cols = set(X.columns)

print("Missing format cols:", expected_cols - actual_cols)
