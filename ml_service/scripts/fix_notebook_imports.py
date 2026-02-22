import json
import glob
import os

def fix_imports_and_remove_custom(nb_path):
    print(f"Processing {nb_path}...")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    filtered_cells = []
    
    for cell in nb['cells']:
        source = cell['source']
        if not source:
            filtered_cells.append(cell)
            continue
            
        source_str = ''.join(source)
        
        # Remove the custom mlflow block I added
        if 'Mendaftarkan model final ke MLflow dan memberikan alias `production`' in source_str:
            print("Removed custom markdown")
            continue
        if 'import mlflow\nfrom mlflow.models.signature import infer_signature' in source_str:
            print("Removed custom mlflow code block")
            continue
            
        # Fix imports
        new_source = []
        for line in source:
            if 'from utils import train_and_register' in line:
                new_source.extend([
                    "import sys\n",
                    "import os\n",
                    "sys.path.append(os.path.abspath('../src/training'))\n"
                ])
                print("Injected sys.path.append")
            new_source.append(line)
        cell['source'] = new_source
        
        filtered_cells.append(cell)
        
    nb['cells'] = filtered_cells
    
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Saved {nb_path}")

for path in glob.glob('notebooks/*.ipynb'):
    fix_imports_and_remove_custom(path)
