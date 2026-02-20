import joblib
import json
from pathlib import Path
from typing import List
import re

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


class ModelLoader:
    def __init__(self):
        self.models = {}
        self.metadata = {}

    def load_models(self):

        def parse_semantic_version(version_str: str):
            """
            Convert v1.2.3 → (1,2,3)
            """
            match = re.match(r"v(\d+)\.(\d+)\.(\d+)", version_str)
            if not match:
                raise ValueError(f"Invalid semantic version format: {version_str}")

            return tuple(map(int, match.groups()))

        for region_path in MODEL_DIR.iterdir():
            if not region_path.is_dir():
                continue

            region_name = region_path.name

            versions = sorted(
                [v for v in region_path.iterdir() if v.is_dir()],
                key=lambda x: parse_semantic_version(x.name)
            )

            if not versions:
                continue

            latest_version = versions[-1]

            model_path = latest_version / "model.pkl"
            metadata_path = latest_version / "metadata.json"

            if not model_path.exists():
                raise Exception(f"[{region_name}] model.pkl not found")

            if not metadata_path.exists():
                raise Exception(f"[{region_name}] metadata.json not found")

            model = joblib.load(model_path)

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # REGION CONSISTENCY CHECK
            metadata_region = metadata.get("region")

            if metadata_region and metadata_region != region_name:
                raise Exception(
                    f"[{region_name}] Region mismatch: "
                    f"folder={region_name}, metadata={metadata_region}"
                )

            # VERSION CONSISTENCY CHECK
            folder_version = latest_version.name
            metadata_version = metadata.get("model_version")

            if folder_version != metadata_version:
                raise Exception(
                    f"[{region_name}] Version mismatch: "
                    f"folder={folder_version}, metadata={metadata_version}"
                )

            # MODEL TYPE CHECK
            if "params" in metadata and "model_type" in metadata["params"]:
                expected_type = metadata["params"]["model_type"]

                if hasattr(model, "named_steps"):
                    actual_type = type(model.named_steps["regressor"]).__name__
                else:
                    actual_type = type(model).__name__

                if actual_type != expected_type:
                    raise Exception(
                        f"[{region_name}] Model type mismatch: "
                        f"expected={expected_type}, actual={actual_type}"
                    )

            # FEATURE CONSISTENCY CHECK
            expected_features = metadata.get("features")

            if expected_features:
                if hasattr(model, "feature_names_in_"):
                    actual_features = list(model.feature_names_in_)

                    if set(actual_features) != set(expected_features):
                        raise Exception(
                            f"[{region_name}] Feature mismatch detected"
                        )

            self.models[region_name] = {
                "model": model,
                "version": folder_version,
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
