"""
Retrain all 4 regional models with the current scikit-learn version
and re-register them in MLflow with the @production alias.

This fixes the pickle incompatibility caused by models trained on
scikit-learn 1.2.2 being loaded in scikit-learn 1.8.0.
"""

import sys
import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Add training utils to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "training"))
from utils import train_and_register

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def load_and_prepare(region: str):
    """Load CSV, clean data, engineer features — mirrors notebook pipeline."""
    csv_path = os.path.join(PROJECT_ROOT, "datasets", f"{region}.csv")
    df = pd.read_csv(csv_path)
    print(f"\n{'='*60}")
    print(f"  REGION: {region}")
    print(f"  Raw shape: {df.shape}")
    print(f"{'='*60}")

    # Drop zero-variance columns
    cols_to_drop = [c for c in df.columns if df[c].nunique() <= 1]
    df = df.drop(columns=cols_to_drop)
    if cols_to_drop:
        print(f"  Dropped zero-variance: {cols_to_drop}")

    # 99th percentile capping on price
    cap = df["harga"].quantile(0.99)
    df = df[df["harga"] <= cap].copy()
    print(f"  After capping (99th={cap:,.0f}): {len(df)} rows")

    # Feature engineering
    df["amenities_count"] = (
        df["is_furnished"].astype(int)
        + df["is_water_heater"].astype(int)
        + df["is_km_dalam"].astype(int)
        + df["is_listrik_free"].astype(int)
        + df["is_mesin_cuci"].astype(int)
        + df["is_parkir_mobil"].astype(int)
    )
    df["luas_kamar"] = df["luas_kamar"].clip(lower=1)

    # Price segments for stratified split
    df["price_segment"] = pd.cut(
        df["harga"],
        bins=[0, 1_500_000, 3_500_000, 6_000_000, 100_000_000],
        labels=["Budget", "Standard", "Upper-Standard", "Premium"],
        duplicates="drop",
    )

    # Features & target
    X = df.drop(columns=["nama_kos", "harga", "price_segment"])
    y = df["harga"].copy()

    print(f"  Features: {list(X.columns)}")
    print(f"  Samples: {len(X)}")

    # Find best split seed (same logic as notebooks)
    candidate_seeds = [42, 123, 456, 789, 2024, 3141, 5678, 9999]
    best_seed = 42
    best_score = float("inf")
    for seed in candidate_seeds:
        _, X_test_cand, _, y_test_cand = train_test_split(
            X, y, test_size=0.2, random_state=seed, stratify=df["price_segment"]
        )
        test_range = y_test_cand.max() - y_test_cand.min()
        test_mean = y_test_cand.mean()
        test_std = y_test_cand.std()
        full_range = y.max() - y.min()
        full_mean = y.mean()
        full_std = y.std()
        score = (
            abs(test_range - full_range) / full_range
            + abs(test_mean - full_mean) / full_mean
            + abs(test_std - full_std) / full_std
        )
        if score < best_score:
            best_score = score
            best_seed = seed

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=best_seed, stratify=df["price_segment"]
    )
    print(f"  Best split seed: {best_seed}")
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    return X_train, X_test, y_train, y_test


def build_preprocessor(continuous_cols):
    """Build the ColumnTransformer matching notebook pipeline."""
    binary_cols = [
        "is_furnished", "is_water_heater", "is_km_dalam",
        "is_listrik_free", "is_mesin_cuci", "is_parkir_mobil",
    ]
    categorical_cols = ["tipe_kos"]

    return ColumnTransformer(
        [
            ("continuous", RobustScaler(), continuous_cols),
            ("binary", "passthrough", binary_cols),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop",
        verbose=0,
    )


def auto_tune(pipeline, param_dist, X_train, y_train, gap_threshold=0.10, n_iter=50):
    """Randomized search with overfitting guard — mirrors notebook auto_tune_healthy."""
    rs = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=n_iter,
        cv=5,
        scoring="r2",
        return_train_score=True,
        n_jobs=-1,
        random_state=RANDOM_SEED,
    )
    print(f"  Searching {n_iter} combinations...")
    rs.fit(X_train, y_train)

    results_df = pd.DataFrame(rs.cv_results_)
    results_df["gap"] = results_df["mean_train_score"] - results_df["mean_test_score"]

    # Filter to healthy candidates (low overfitting gap)
    healthy = results_df[results_df["gap"] <= gap_threshold]
    if len(healthy) > 0:
        best_idx = healthy["mean_test_score"].idxmax()
    else:
        best_idx = results_df["mean_test_score"].idxmax()

    best_params = results_df.loc[best_idx, "params"]
    best_pipeline = pipeline.set_params(**best_params)
    best_pipeline.fit(X_train, y_train)

    print(f"  Best R² (CV): {results_df.loc[best_idx, 'mean_test_score']:.4f}")
    print(f"  Gap: {results_df.loc[best_idx, 'gap']:.4f}")
    return best_pipeline, best_params


def train_region(region, X_train, X_test, y_train, y_test):
    """Train a model for a region and register it in MLflow."""
    continuous_cols_tree = ["jarak_ke_bca", "luas_kamar", "amenities_count"]
    preprocessor = build_preprocessor(continuous_cols_tree)

    # RandomForest tuning (used by all regions in notebooks)
    rf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(random_state=RANDOM_SEED, n_jobs=-1)),
    ])

    param_dist_rf = {
        "regressor__max_depth": [5, 8, 10, 12, 15, 20],
        "regressor__n_estimators": [150, 200, 250],
        "regressor__min_samples_leaf": [2, 4, 8],
        "regressor__max_features": ["sqrt", "log2"],
    }

    print(f"\n  --- Random Forest Tuning ---")
    rf_tuned, rf_params = auto_tune(rf_pipeline, param_dist_rf, X_train, y_train)

    # Gradient Boosting tuning
    gb_pipeline = Pipeline([
        ("preprocessor", build_preprocessor(continuous_cols_tree)),
        ("regressor", GradientBoostingRegressor(random_state=RANDOM_SEED)),
    ])

    param_dist_gb = {
        "regressor__max_depth": [2, 3, 4, 5, 6],
        "regressor__n_estimators": [100, 150, 200, 250],
        "regressor__learning_rate": [0.01, 0.05, 0.1, 0.15],
        "regressor__subsample": [0.7, 0.8, 0.9],
        "regressor__min_samples_leaf": [2, 4, 8],
    }

    print(f"\n  --- Gradient Boosting Tuning ---")
    gb_tuned, gb_params = auto_tune(gb_pipeline, param_dist_gb, X_train, y_train)

    # Compare and pick the best
    rf_pred = rf_tuned.predict(X_test)
    gb_pred = gb_tuned.predict(X_test)

    rf_r2 = r2_score(y_test, rf_pred)
    gb_r2 = r2_score(y_test, gb_pred)

    if rf_r2 >= gb_r2:
        final_model = rf_tuned
        y_pred = rf_pred
        best_params = rf_params
        model_type = "RandomForestRegressor"
        print(f"\n  Winner: Random Forest (R²={rf_r2:.4f} vs GB R²={gb_r2:.4f})")
    else:
        final_model = gb_tuned
        y_pred = gb_pred
        best_params = gb_params
        model_type = "GradientBoostingRegressor"
        print(f"\n  Winner: Gradient Boosting (R²={gb_r2:.4f} vs RF R²={rf_r2:.4f})")

    # Compute metrics
    final_mae = mean_absolute_error(y_test, y_pred)
    final_r2 = r2_score(y_test, y_pred)
    final_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    final_mape = float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100)

    print(f"  R²:   {final_r2:.4f}")
    print(f"  MAE:  Rp {final_mae:,.0f}")
    print(f"  RMSE: Rp {final_rmse:,.0f}")
    print(f"  MAPE: {final_mape:.2f}%")

    # Register in MLflow
    params = {"model_type": model_type}
    params.update({str(k): str(v) for k, v in best_params.items()})

    metrics = {
        "MAE": final_mae,
        "R2": final_r2,
        "RMSE": final_rmse,
        "MAPE": final_mape,
    }

    model_uri = train_and_register(
        region=region,
        model=final_model,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        params=params,
        metrics=metrics,
    )

    print(f"  Registered at: {model_uri}")
    return model_uri


def main():
    regions = ["jakarta_pusat", "jakarta_selatan", "jakarta_utara", "yogyakarta"]
    results = {}

    for region in regions:
        X_train, X_test, y_train, y_test = load_and_prepare(region)
        uri = train_region(region, X_train, X_test, y_train, y_test)
        results[region] = uri

    print(f"\n{'='*60}")
    print("  ALL MODELS RETRAINED SUCCESSFULLY")
    print(f"{'='*60}")
    for region, uri in results.items():
        print(f"  {region}: {uri}")


if __name__ == "__main__":
    main()
