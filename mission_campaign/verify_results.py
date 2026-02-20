import os
import sqlite3
import pandas as pd
import json

def verify_db():
    db_path = "research_database/mission_data.db"
    if not os.path.exists(db_path):
        print("DB not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM campaign_runs")
    count = cursor.fetchone()[0]
    print(f"Total Runs in DB: {count}")
    
    if count > 0:
        cursor.execute("SELECT run_id, final_energy, escape_flag, duration_seconds FROM campaign_runs LIMIT 1")
        row = cursor.fetchone()
        print(f"Sample Run: {row}")
    conn.close()

def verify_files(run_id='run_000000'):
    base_dir = "test_campaign_data"
    run_dir = os.path.join(base_dir, run_id)
    
    if not os.path.exists(run_dir):
        print(f"Directory {run_dir} not found!")
        return

    meta_path = os.path.join(run_dir, "run_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        print(f"Metadata Status: {meta.get('execution', {}).get('status')}")
    else:
        print("Metadata file missing!")

    traj_path = os.path.join(run_dir, "trajectory.parquet")
    if os.path.exists(traj_path):
        try:
            df = pd.read_parquet(traj_path)
            print(f"Trajectory Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"Error reading parquet: {e}")
    else:
        print("Trajectory file missing!")

if __name__ == "__main__":
    print("--- Database Verification ---")
    verify_db()
    print("\n--- File Verification ---")
    verify_files()
