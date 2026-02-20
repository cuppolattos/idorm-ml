import mlflow
import mlflow.sklearn
import json
import joblib
from pathlib import Path
from versioning import get_next_version


def train_and_register(
    region: str,
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    params: dict,
    metrics: dict,
    bump="patch",
    base_model_dir="models"
):

    mlflow.set_experiment(f"{region}_experiment")

    with mlflow.start_run() as run:

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(model, "model")

        run_id = run.info.run_id

        model_name = f"{region}_model"
        mlflow.register_model(
            f"runs:/{run_id}/model",
            model_name
        )

        export_model(
            region,
            model,
            params,
            metrics,
            run_id,
            bump,
            base_model_dir
        )


def export_model(region, model, params, metrics, run_id, bump, base_model_dir):

    region_path = Path(base_model_dir) / region
    region_path.mkdir(parents=True, exist_ok=True)

    next_version = get_next_version(region_path, bump=bump)

    export_path = region_path / next_version
    export_path.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, export_path / "model.pkl")

    metadata = {
        "mlflow_run_id": run_id,
        "model_version": next_version,
        "params": params,
        "metrics": metrics
    }

    with open(export_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Exported {region} {next_version}")
