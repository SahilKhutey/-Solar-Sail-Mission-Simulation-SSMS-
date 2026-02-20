import os
import sys
from datetime import datetime
import pandas as pd
import sqlite3

# Ensure imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reporting_engine.figure_generator import FigureGenerator
from research_database.db_manager import DatabaseManager

class ReportBuilder:
    def __init__(self, campaign_id: str, base_dir: str, db_path: str = None):
        self.campaign_id = campaign_id
        self.base_dir = base_dir
        self.report_dir = os.path.join(base_dir, 'reports', campaign_id)
        self.data_dir = os.path.join(base_dir, 'campaign_data') # Assuming standard structure
        self.db_path = db_path if db_path else os.path.join(base_dir, 'research_database', 'mission_data.db')
        print(f"DEBUG: ReportBuilder data_dir={self.data_dir} db_path={self.db_path}")
        
    def _export_csv(self):
        """Exports campaign data to CSV."""
        print("Exporting CSV data...")
        csv_path = os.path.join(self.report_dir, 'campaign_summary.csv')
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=60)
            df = pd.read_sql_query("SELECT * FROM campaign_runs", conn)
            df.to_csv(csv_path, index=False)
            conn.close()
            print(f"CSV exported to {csv_path}")
        except Exception as e:
            print(f"Failed to export CSV: {e}")

    def _export_csv(self):
        """Exports campaign data to CSV."""
        print("Exporting CSV data...")
        csv_path = os.path.join(self.report_dir, 'campaign_summary.csv')
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=60)
            df = pd.read_sql_query("SELECT * FROM campaign_runs", conn)
            df.to_csv(csv_path, index=False)
            conn.close()
            print(f"CSV exported to {csv_path}")
        except Exception as e:
            print(f"Failed to export CSV: {e}")

    def build(self):
        print(f"Building report for {self.campaign_id}...")
        os.makedirs(self.report_dir, exist_ok=True)
        
        # 1. Generate Figures
        fig_gen = FigureGenerator(self.db_path, self.data_dir, self.report_dir)
        
        # Campaign Level
        print("Generating campaign summary plots...")
        fig_gen.generate_campaign_summary()
        
        # Run Level (Top 3 performing?)
        # Fetch best runs from DB
        db = DatabaseManager(self.db_path)
        runs = db.get_completed_runs(self.campaign_id)
        
        # Sort by final energy (descending), handling None values
        runs.sort(key=lambda x: x.get('final_energy') if x.get('final_energy') is not None else -float('inf'), reverse=True)
        top_runs = runs[:3]
        
        print(f"Generating plots for top {len(top_runs)} runs...")
        for run in top_runs:
            run_id = run['run_id']
            fig_gen.generate_run_plots(run_id)
            
        # 2. Export CSV
        self._export_csv()

        # 3. Compile Markdown/LaTeX
        self._generate_markdown_summary(runs, top_runs)
        
        print(f"Report generated in {self.report_dir}")

    def _generate_markdown_summary(self, all_runs, top_runs):
        path = os.path.join(self.report_dir, 'executive_summary.md')
        
        total = len(all_runs)
        escaped = sum(1 for r in all_runs if r.get('escape_flag'))
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Campaign Report: {self.campaign_id}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write("## 1. Executive Summary\n")
            f.write(f"- **Total Simulations:** {total}\n")
            f.write(f"- **Successful Escapes:** {escaped}\n")
            if total > 0:
                f.write(f"- **Success Rate:** {escaped/total*100:.1f}%\n\n")
            else:
                f.write(f"- **Success Rate:** N/A (0 runs)\n\n")
            
            f.write("## 2. Design Space Analysis\n")
            f.write("![Design Space](campaign_area_mass_energy.png)\n\n")
            f.write("![Escape Regions](campaign_escape_regions.png)\n\n")
            f.write("![Energy Distribution](campaign_energy_hist.png)\n\n")
            f.write("![3D Design Landscape](campaign_design_space_3d.png)\n\n")
            
            f.write("## 3. Best Performing Missions\n")
            for i, run in enumerate(top_runs):
                rid = run['run_id']
                f.write(f"### Rank {i+1}: {rid}\n")
                f.write(f"- **Final Energy:** {run.get('final_energy', 0):.2e} J\n")
                f.write(f"- **Parameters:** Area={run.get('sail_area')} m², Mass={run.get('mass')} kg\n")
                f.write(f"- **Plots:**\n")
                f.write(f"  - ![Trajectory]({rid}/distance_vs_time.png)\n")
                f.write(f"  - ![3D Orbit]({rid}/trajectory_3d.png)\n")
                f.write(f"  - ![Energy]({rid}/energy_vs_time.png)\n\n")
            
            f.write("\n_Generated by Auto-Reporting Engine_")

if __name__ == "__main__":
    # Example usage
    # Ideally passed via CLI
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('campaign_name', help="Name of campaign to report on")
    parser.add_argument('--base_dir', default='.', help="Project base directory")
    parser.add_argument('--db_path', default=None, help="Custom path to database")
    args = parser.parse_args()
    
    builder = ReportBuilder(args.campaign_name, args.base_dir, args.db_path)
    builder.build()
