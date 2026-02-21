import mlflow.sklearn
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MLFLOW_DB = os.path.join(_PROJECT_ROOT, "notebooks", "mlflow.db")
_MLFLOW_URI = "sqlite:///" + _MLFLOW_DB.replace("\\", "/")


def _get_current_semver(client, model_name):
    """Read the latest semantic version from the production alias tags."""
    try:
        mv = client.get_model_version_by_alias(model_name, "production")
        return mv.tags.get("semantic_version", "v1.0.0")
    except Exception:
        return "v0.0.0"  # No production model yet


def _bump_semver(current: str, bump: str = "patch") -> str:
    """
    Bump a semantic version string.
      bump='major' -> v2.0.0
      bump='minor' -> v1.1.0
      bump='patch' -> v1.0.1
    """
    # Strip leading 'v' if present
    ver = current.lstrip("v")
    parts = ver.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    return f"v{major}.{minor}.{patch}"


def train_and_register(region, model, X_train, y_train, X_test, y_test, params, metrics, bump="patch"):
    """
    Train, log metrics, register model in MLflow, set @production alias,
    and tag with a semantic version (vMAJOR.MINOR.PATCH).

    bump: 'major' | 'minor' | 'patch' — controls version increment.
      - major: architecture/model type change
      - minor: performance improvement
      - patch: bug fix or preprocessing adjustment
    """
    mlflow.set_tracking_uri(_MLFLOW_URI)
    model_name = f"{region}_model"

    client = MlflowClient()

    # Determine next semantic version
    current_semver = _get_current_semver(client, model_name)
    next_semver = _bump_semver(current_semver, bump)

    with mlflow.start_run(run_name=f"{region}_final"):
        # Log params & metrics
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.set_tag("semantic_version", next_semver)

        # Log model with signature
        signature = infer_signature(X_test, model.predict(X_test))
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=model_name,
            signature=signature
        )

        # Set @production alias
        client.set_registered_model_alias(
            name=model_name,
            alias="production",
            version=model_info.registered_model_version
        )

        # Tag the model version with semantic version
        client.set_model_version_tag(
            name=model_name,
            version=model_info.registered_model_version,
            key="semantic_version",
            value=next_semver
        )

        print(f"  [{region}] Registered {model_name} version {model_info.registered_model_version} "
              f"(semantic: {next_semver}, bump: {bump})")

        return model_info.model_uri