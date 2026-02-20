import os
import pandas as pd
import numpy as np
import sqlite3
import shutil
from datetime import datetime

def generate_dummy_data(base_dir="campaign_data", num_runs=5):
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = "research_database/mission_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Generating {num_runs} dummy runs...")
    
    for i in range(num_runs):
        run_id = f"run_{i:06d}"
        run_dir = os.path.join(base_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)
        
        # 1. Create Parquet
        t = np.linspace(0, 10*86400, 100)
        # Heliocentric toy orbit
        r_au = 1.0 + 0.1 * np.sin(2 * np.pi * t / (365*86400)) + 0.05 * (i/num_runs) * t/86400/100
        angle = 2 * np.pi * t / (365*86400)
        x = r_au * np.cos(angle) * 1.496e8
        y = r_au * np.sin(angle) * 1.496e8
        z = np.zeros_like(x)
        
        vx = -29.78 * np.sin(angle)
        vy = 29.78 * np.cos(angle)
        vz = np.zeros_like(x)
        
        df = pd.DataFrame({
            'time': t,
            'x': x, 'y': y, 'z': z,
            'vx': vx, 'vy': vy, 'vz': vz,
            'energy': -398600 / (r_au * 1.496e8) # Dummy energy
        })
        
        df.to_parquet(os.path.join(run_dir, "trajectory.parquet"))
        
        # 2. Insert into DB
        # Check if exists to avoid overwriting real data if it happened to finish
        cursor.execute("SELECT 1 FROM campaign_runs WHERE run_id = ?", (run_id,))
        if cursor.fetchone():
            print(f"Run {run_id} already in DB, skipping insert.")
            continue
            
        data = {
            'run_id': run_id,
            'campaign_id': "Test_Verification_Campaign",
            'sail_area': 1000 + i * 500,
            'mass': 50 + i * 10,
            'reflectivity': 0.9,
            'thickness': 5.0,
            'launch_altitude': 500,
            'steering_law': 'fixed',
            'time_of_flight': 10.0,
            'final_energy': -1e5 + i*1000,
            'escape_velocity': 0,
            'max_stress': 100,
            'max_temp': 300,
            'min_distance_sun': 1.0,
            'escape_flag': False,
            'structural_failure': False,
            'thermal_failure': False,
            'stability_score': 1.0,
            'convergence_flag': True,
            'duration_seconds': 1.5,
            'start_time': datetime.now().isoformat(),
            'git_hash': 'dummy_hash'
        }
        
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO campaign_runs ({cols}) VALUES ({placeholders})"
        cursor.execute(sql, list(data.values()))
        
    conn.commit()
    conn.close()
    print("Dummy data generation complete.")

if __name__ == "__main__":
    generate_dummy_data()
