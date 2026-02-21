import json
import glob
import os

mlflow_code_template = """import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
import warnings
warnings.filterwarnings('ignore')

mlflow.set_tracking_uri("sqlite:///../mlflow.db")
region_name = "{region}"
model_name = f"{region_name}_model"

with mlflow.start_run(run_name=f"{region_name}_training"):
    # Infer signature from training data
    signature = infer_signature(X_train, y_train)
    
    # Register model
    model_info = mlflow.sklearn.log_model(
        sk_model=final_model,
        artifact_path="model",
        signature=signature,
        registered_model_name=model_name
    )
    
    # Assign production alias
    client = MlflowClient()
    client.set_registered_model_alias(
        name=model_name,
        alias="production",
        version=model_info.registered_model_version
    )
    
    print(f"Successfully registered {model_name} version {model_info.registered_model_version} as production.")
"""

def add_mlflow_cells(nb_path):
    print(f"Processing {nb_path}...")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    region = os.path.basename(nb_path).replace('2.ipynb', '')
    
    # Check if we already added it
    if any('import mlflow' in ''.join(cell['source']) and 'set_tracking_uri' in ''.join(cell['source']) for cell in nb['cells']):
        print(f"Already contains MLflow code: {nb_path}")
        return
        
    markdown_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 9. Model Registration (MLflow)\n",
            "Mendaftarkan model final ke MLflow dan memberikan alias `production`."
        ]
    }
    
    code_content = mlflow_code_template.replace("{region}", region)
    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + '\n' for line in code_content.split('\n')]
    }
    
    nb['cells'].append(markdown_cell)
    nb['cells'].append(code_cell)
    
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Updated {nb_path}")

for path in glob.glob('notebooks/*.ipynb'):
    add_mlflow_cells(path)
