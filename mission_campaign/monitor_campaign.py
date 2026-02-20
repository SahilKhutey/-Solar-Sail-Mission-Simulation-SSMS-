import sqlite3
import os
import sys
import yaml
import time
from datetime import datetime

def monitor(config_path="mission_campaign/campaign_config.yaml"):
    # Load config to get target number
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    target = config['sampling']['num_samples']
    base_dir = config['output'].get('base_dir', 'campaign_data')
    db_path = "research_database/mission_data.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Monitoring Campaign: {config.get('campaign_name', 'Unknown')}")
    print(f"Target Runs: {target}")
    print("-" * 40)
    
    try:
        # Check DB count (Only completed runs are logged)
        cursor.execute("SELECT COUNT(*) FROM campaign_runs")
        completed = cursor.fetchone()[0]
        
        # Failed runs are not currently logged in DB, but we can infer from files if needed
        # or just report 0 for now as we don't store failures.
        failed = 0 
        
        # Check files (approximate)
        if os.path.exists(base_dir):
            dirs = [d for d in os.listdir(base_dir) if d.startswith('run_')]
            files_count = len(dirs)
        else:
            files_count = 0
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Status Update:")
        print(f"  Runs Successfully Logged in DB: {completed}/{target} ({(completed/target)*100:.1f}%)")
        print(f"  Failed Runs in DB:            {failed}")
        print(f"  Run Directories Created:      {files_count}")
        
        if completed >= target:
            print("\n✅ Campaign Complete!")
        elif completed + failed >= target:
            print("\n⚠️  Campaign Finished with Failures.")
        else:
            print("\n🔄 Campaign In Progress...")
            
    except Exception as e:
        print(f"Error monitoring: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "mission_campaign/campaign_config.yaml"
    monitor(path)
