import joblib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


class ModelLoader:
    def __init__(self):
        self.models = {}
        self.metadata = {}

    def load_models(self):
        for region_path in MODEL_DIR.iterdir():
            if region_path.is_dir():

                region_name = region_path.name

                versions = sorted(
                    [v for v in region_path.iterdir() if v.is_dir()],
                    key=lambda x: x.name
                )

                if not versions:
                    continue

                latest_version = versions[-1]

                model_path = latest_version / "model.pkl"
                metadata_path = latest_version / "metadata.json"

                model = joblib.load(model_path)

                metadata = {}
                if metadata_path.exists():
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                self.models[region_name] = {
                    "model": model,
                    "version": latest_version.name,
                    "metadata": metadata
                }

        print(f"Loaded models: {list(self.models.keys())}")

    def get_model(self, region: str):
        return self.models.get(region)

    def get_model_info(self, region: str):
        return self.models.get(region)

    def get_metadata(self, region: str):
        region_data = self.models.get(region)
        if region_data:
            return region_data["metadata"]
        return None

model_loader = ModelLoader()
