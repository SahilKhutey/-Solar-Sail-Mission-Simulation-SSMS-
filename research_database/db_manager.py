import sqlite3
import os
import json
from typing import Dict, Any, List

class DatabaseManager:
    """
    Manages the SQLite research database.
    """
    def __init__(self, db_path: str = "research_database/mission_data.db", schema_path: str = "research_database/schema.sql"):
        self.db_path = db_path
        self.schema_path = schema_path
        self._init_db()

    def _init_db(self):
        """Initializes the database with the schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=60)
        cursor = conn.cursor()
        
        # Read schema
        if os.path.exists(self.schema_path):
            with open(self.schema_path, 'r') as f:
                schema = f.read()
            cursor.executescript(schema)
        else:
            print(f"Schema file not found at {self.schema_path}. Tables might not be created.")
            
        conn.commit()
        conn.close()

    def insert_run(self, run_data: Dict[str, Any]):
        """
        Inserts a new run into the campaign_runs table.
        """
        conn = sqlite3.connect(self.db_path, timeout=60)
        cursor = conn.cursor()
        
        # Extract keys that match the schema roughly
        # This assumes run_data has keys matching table columns or we map them here
        
        query = """
        INSERT OR REPLACE INTO campaign_runs (
            run_id, campaign_id, sail_area, mass, reflectivity, thickness, 
            launch_altitude, steering_law, time_of_flight, final_energy, 
            escape_velocity, max_stress, max_temp, min_distance_sun,
            escape_flag, structural_failure, thermal_failure, stability_score,
            convergence_flag, duration_seconds, start_time, git_hash
        ) VALUES (
            :run_id, :campaign_id, :sail_area, :sail_mass, :reflectivity, :thickness,
            :launch_altitude, :steering_law, :time_of_flight, :final_energy,
            :escape_velocity, :max_stress, :max_temp, :min_distance_sun,
            :escape_flag, :structural_failure, :thermal_failure, :stability_score,
            :convergence_flag, :duration_seconds, :start_time, :git_hash
        )
        """
        try:
            cursor.execute(query, run_data)
            conn.commit()
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
        finally:
            conn.close()

    def get_completed_runs(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Returns list of completed runs for a campaign."""
        conn = sqlite3.connect(self.db_path, timeout=60)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM campaign_runs WHERE campaign_id = ?", (campaign_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def close(self):
        pass
