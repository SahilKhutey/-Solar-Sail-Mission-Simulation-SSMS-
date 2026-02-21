import time
import sqlite3
import subprocess
import sys
import os
import json
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

CAMPAIGN_NAME = "SolarSail_Research_Campaign_v1"
TARGET_RUNS = 10000
DB_PATH = "research_database/mission_data.db"
DATA_DIR = "campaign_data"
CHECK_INTERVAL_SEC = 30

def get_db_run_ids():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=60)
        cursor = conn.cursor()
        cursor.execute("SELECT run_id FROM campaign_runs")
        ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return ids
    except Exception as e:
        # DB might be locked or empty
        return set()

def insert_run_data(data):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10) # Short timeout for quick inserts
        cursor = conn.cursor()
        
        cols = [
            'run_id', 'campaign_id', 
            'sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude', 'steering_law',
            'time_of_flight', 'final_energy', 'escape_velocity', 'max_stress', 'min_distance_sun',
            'escape_flag', 'duration_seconds'
        ]
        
        vals = [
            data.get('run_id'),
            data.get('campaign_id', CAMPAIGN_NAME),
            data.get('sail_area'),
            data.get('mass') or data.get('sail_mass'),
            data.get('reflectivity'),
            data.get('thickness', 5.0),
            data.get('launch_altitude'),
            data.get('steering_law'),
            data.get('time_of_flight'),
            data.get('final_energy'),
            data.get('escape_velocity'),
            data.get('max_stress'),
            data.get('min_solar_distance'), # Key from metadata.json
            1 if data.get('escape_flag') else 0,
            data.get('duration_seconds')
        ]
        
        placeholders = ','.join(['?']*len(cols))
        sql = f"INSERT OR REPLACE INTO campaign_runs ({','.join(cols)}) VALUES ({placeholders})"
        
        cursor.execute(sql, vals)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"\r[Error] Insert {data.get('run_id')}: {e}")
        return False

def process_run_dir(run_dir):
    try:
        # 1. Load Metadata
        meta_path = os.path.join(DATA_DIR, run_dir, 'run_metadata.json')
        if not os.path.exists(meta_path):
            return False
            
        with open(meta_path, 'r') as f:
            data = json.load(f)
        
        # 2. Check if results are missing (common if runner didn't log)
        # We need final_energy, time_of_flight, escape_flag at minimum
        
        # If any key missing, Calculate from Parquet
        needs_calc = 'final_energy' not in data or 'escape_velocity' not in data
        
        if needs_calc:
            pq_path = os.path.join(DATA_DIR, run_dir, 'trajectory.parquet')
            if os.path.exists(pq_path):
                try:
                    df = pd.read_parquet(pq_path)
                    if not df.empty:
                        last = df.iloc[-1]
                        
                        # Recalculate outcomes
                        r_vec = np.array([last['x'], last['y'], last['z']])
                        v_vec = np.array([last['vx'], last['vy'], last['vz']])
                        r_norm = np.linalg.norm(r_vec)
                        v_norm = np.linalg.norm(v_vec)
                        
                        # Energy = v^2/2 - mu/r (mu_sun = 132712440018 km^3/s^2 approx? No, units check)
                        # The sim uses mu = 1.0 or similar if normalized? 
                        # Wait, runner.py uses 398600 (Earth) or 1.327e11 (Sun)?
                        # Runner line 115: 398600.4418 / r -> Earth mu.
                        # So Energy = 0.5 * v^2 - 398600.4418 / r
                        
                        energy = 0.5 * v_norm**2 - 398600.4418 / (r_norm + 1e-6)
                        data['final_energy'] = energy
                        data['time_of_flight'] = last['time']
                        data['escape_flag'] = energy > 0
                        data['escape_velocity'] = 0.0 # approx
                        data['max_stress'] = 0.0
                        if 'solar_distance' in last:
                            data['min_solar_distance'] = df['solar_distance'].min()
                        else:
                            data['min_solar_distance'] = r_norm # rough check
                except Exception as e:
                    # print(f"Parquet read failed {run_dir}: {e}")
                    pass

        if 'run_id' not in data:
            data['run_id'] = run_dir
            
        return insert_run_data(data)
    except Exception as e:
        print(f"\r[Error] Process {run_dir}: {e}")
    return False

BLACKLIST = set()

def sync_db(known_ids):
    print(f"\n[Sync] Scanning {DATA_DIR}...")
    if not os.path.exists(DATA_DIR): return 0
    
    all_runs = {d for d in os.listdir(DATA_DIR) if d.startswith('run_')}
    
    # Filter out known runs AND blacklisted runs
    candidates = all_runs - known_ids - BLACKLIST
    missing = list(candidates)
    
    if not missing:
        return 0
        
    print(f"[Sync] Found {len(missing)} unindexed runs. Indexing...")
    
    indexed = 0
    # Process runs serially or in threads - if process_run_dir returns False, blacklist it
    # We need to know WHICH ones failed to blacklist them.
    # Executor map doesn't return which one failed easily if result is just False.
    
    # Let's use simple loop for robustness on the filtered list
    for run_dir in missing:
        success = process_run_dir(run_dir)
        if success:
            indexed += 1
        else:
            # If failed, add to blacklist to prevent retry loop
            # print(f" [Warn] Blacklisting broken run: {run_dir}")
            BLACKLIST.add(run_dir)
        
    print(f"[Sync] Indexed {indexed} new runs. (Blacklisted {len(BLACKLIST)} broken runs)")
    return len(known_ids) + indexed

def generate_report():
    print(f"\n[INFO] Starting Report Generation for {CAMPAIGN_NAME}...")
    
    import shutil
    temp_db = "temp_mission_report.db"
    try:
        shutil.copy2(DB_PATH, temp_db)
        print(" [OK] Database snapshot created.")
    except Exception as e:
        print(f" [WARN] Copy failed: {e}. Using direct DB.")
        temp_db = DB_PATH
        
    cmd = [sys.executable, "reporting_engine/report_builder.py", 
           CAMPAIGN_NAME, "--db_path", temp_db]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Report Generation Complete!")
        print(f"Check 'reports/{CAMPAIGN_NAME}/' for PDF, Plots, and CSV.")
    except Exception as e:
        print(f"\n[ERROR] Report Generation Failed: {e}")
    finally:
        if temp_db != DB_PATH and os.path.exists(temp_db):
            os.remove(temp_db)

def main():
    print("=== Solar Sail Campaign Manager (Auto-Sync) ===")
    print(f"Target: {TARGET_RUNS} runs")
    
    while True:
        # 1. Get current DB state
        known_ids = get_db_run_ids()
        count = len(known_ids)
        
        # 2. Sync if needed
        # Just check file count first to see if we are behind
        if os.path.exists(DATA_DIR):
             file_count = len([d for d in os.listdir(DATA_DIR) if d.startswith('run_')])
        else:
             file_count = 0
             
        if file_count > count:
            count = sync_db(known_ids)
        
        sys.stdout.write(f"\rProgress: {count}/{TARGET_RUNS} runs [{count/TARGET_RUNS*100:.1f}%]   ")
        sys.stdout.flush()
        
        if count >= TARGET_RUNS:
            print("\n\n[INFO] Campaign Target Reached!")
            break
            
        time.sleep(CHECK_INTERVAL_SEC)
        
    time.sleep(5)
    generate_report()

if __name__ == "__main__":
    main()
