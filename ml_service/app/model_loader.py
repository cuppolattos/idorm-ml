import mlflow.pyfunc
import threading
import logging
import os
from pathlib import Path
from mlflow.tracking import MlflowClient

logger = logging.getLogger("inference")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MLFLOW_DB = os.path.join(_PROJECT_ROOT, "notebooks", "mlflow.db")
_MLFLOW_URI = "sqlite:///" + _MLFLOW_DB.replace("\\", "/")
mlflow.set_tracking_uri(_MLFLOW_URI)

# Auto-upgrade MLflow DB schema on import to prevent version mismatch errors.
# Uses a short timeout so concurrent processes don't block each other.
try:
    from mlflow.store.db.utils import _upgrade_db
    from sqlalchemy import create_engine
    engine = create_engine(_MLFLOW_URI, connect_args={"timeout": 5})
    _upgrade_db(engine)
    engine.dispose()
except Exception as _e:
    print(f"[model_loader] MLflow DB auto-upgrade skipped: {_e}")


class ModelProvider:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelProvider, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.models = {}
        self.models_lock = threading.Lock()
        self._initialized = True

    def load_models(self):
        regions = ["jakarta_pusat", "jakarta_selatan", "jakarta_utara", "yogyakarta"]

        with self.models_lock:
            for region in regions:
                model_uri = f"models:/{region}_model@production"
                try:
                    logger.info("loading_model", extra={"region": region, "model_uri": model_uri})
                    model = mlflow.pyfunc.load_model(model_uri=model_uri)

                    # Fetch version info via MLflow client
                    client = MlflowClient()

                    try:
                        mv = client.get_model_version_by_alias(f"{region}_model", "production")
                        # Read semantic version from tags, fallback to MLflow integer version
                        sem_ver = mv.tags.get("semantic_version", None)
                        version_str = sem_ver if sem_ver else f"v{mv.version}"
                    except Exception:
                        version_str = "production"

                    self.models[region] = {
                        "model": model,
                        "version": version_str,
                        "metadata": getattr(model, "metadata", None)
                    }

                    from app.metrics import MODEL_LOAD_STATUS
                    MODEL_LOAD_STATUS.labels(region=region).set(1)

                    print(f"[{region}] Successfully loaded model version {version_str}")
                except Exception as e:
                    logger.error("model_load_error", extra={"region": region, "error": str(e)})
                    print(f"[{region}] FAILED to load: {e}")
                    from app.metrics import MODEL_LOAD_STATUS
                    MODEL_LOAD_STATUS.labels(region=region).set(0)

    def get_model(self, region: str):
        with self.models_lock:
            return self.models.get(region)

    def get_model_info(self, region: str):
        with self.models_lock:
            info = self.models.get(region)
            if info:
                return {
                    "version": info["version"],
                    "metadata": info["metadata"].to_dict() if info["metadata"] else {}
                }
            return None


model_loader = ModelProvider()
