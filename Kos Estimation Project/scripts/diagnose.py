import sqlite3
import os

# Check root mlflow.db
print("=== ROOT mlflow.db ===")
conn = sqlite3.connect("mlflow.db")
c = conn.cursor()

print("\n--- Registered Models ---")
c.execute("SELECT name, creation_time, last_updated_time FROM registered_models")
for row in c.fetchall():
    print(f"  {row}")

print("\n--- Model Versions ---")
c.execute("SELECT name, version, current_stage, source, run_id FROM model_versions")
for row in c.fetchall():
    print(f"  {row}")

print("\n--- Model Aliases ---")
c.execute("SELECT name, alias, version FROM registered_model_aliases")
for row in c.fetchall():
    print(f"  {row}")

print("\n--- Runs ---")
c.execute("SELECT run_uuid, experiment_id, status, artifact_uri FROM runs LIMIT 10")
for row in c.fetchall():
    print(f"  {row}")

conn.close()

# Check notebooks mlflow.db
print("\n\n=== NOTEBOOKS mlflow.db ===")
conn2 = sqlite3.connect("notebooks/mlflow.db")
c2 = conn2.cursor()

print("\n--- Registered Models ---")
c2.execute("SELECT name, creation_time, last_updated_time FROM registered_models")
for row in c2.fetchall():
    print(f"  {row}")

print("\n--- Model Versions ---")
c2.execute("SELECT name, version, current_stage, source, run_id FROM model_versions")
for row in c2.fetchall():
    print(f"  {row}")

print("\n--- Model Aliases ---")
c2.execute("SELECT name, alias, version FROM registered_model_aliases")
for row in c2.fetchall():
    print(f"  {row}")

print("\n--- Runs ---")
c2.execute("SELECT run_uuid, experiment_id, status, artifact_uri FROM runs LIMIT 10")
for row in c2.fetchall():
    print(f"  {row}")

conn2.close()

# Check if mlruns directory exists at root
print("\n\n=== DIRECTORY CHECK ===")
print(f"Root mlruns exists: {os.path.isdir('mlruns')}")
print(f"Notebooks mlruns exists: {os.path.isdir('notebooks/mlruns')}")
if os.path.isdir("mlruns"):
    for item in os.listdir("mlruns"):
        print(f"  mlruns/{item}")
if os.path.isdir("notebooks/mlruns"):
    for item in os.listdir("notebooks/mlruns"):
        subpath = os.path.join("notebooks/mlruns", item)
        print(f"  notebooks/mlruns/{item} (dir={os.path.isdir(subpath)})")
