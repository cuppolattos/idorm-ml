import json
import os

def update_nb(filepath):
    print(f"Updating {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            for i, line in enumerate(source):
                if 'features_to_drop =' in line and 'jarak_ke_bca' in line:
                    source[i] = "features_to_drop = ['proximity_score', 'is_walking_dist']\n"
                    print("Updated features_to_drop")
                
                if line.startswith("continuous_cols_linear ="):
                    if "'jarak_ke_bca'" not in line:
                        source[i] = "continuous_cols_linear = ['luas_kamar', 'jarak_ke_bca']\n"
                        print("Updated continuous_cols_linear")
                        
    # save
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f)
    print("Saved.")

update_nb('notebooks/jakarta_selatan2.ipynb')
update_nb('notebooks/jakarta_utara2.ipynb')
