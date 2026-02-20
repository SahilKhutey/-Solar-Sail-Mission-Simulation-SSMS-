import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Dict

class FigureGenerator:
    """
    Generates static figures for the mission campaign report.
    """
    def __init__(self, db_path: str, data_dir: str, output_dir: str):
        self.db_path = db_path
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_run_plots(self, run_id: str):
        """Generates standard plots for a single run."""
        output_sub_dir = os.path.join(self.output_dir, run_id)
        os.makedirs(output_sub_dir, exist_ok=True)
        
        # Load data
        parquet_path = os.path.join(self.data_dir, run_id, "trajectory.parquet")
        if not os.path.exists(parquet_path):
            print(f"Data not found for {run_id} at {parquet_path}")
            return

        df = pd.read_parquet(parquet_path)
        
        # 1. Trajectory (3D view projected or 2D) - Distance vs Time
        self._plot_distance(df, run_id, output_sub_dir)
        
        # 2. Energy
        self._plot_energy(df, run_id, output_sub_dir)
        
        # 3. Velocity
        self._plot_velocity(df, run_id, output_sub_dir)

        # 4. 3D Trajectory
        self._plot_trajectory_3d(df, run_id, output_sub_dir)

    def _plot_trajectory_3d(self, df, run_id, out_dir):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Convert to AU
        x_au = df['x'] / 1.496e8
        y_au = df['y'] / 1.496e8
        z_au = df['z'] / 1.496e8
        
        ax.plot(x_au, y_au, z_au, label='Trajectory')
        
        # Plot Sun
        ax.scatter([0], [0], [0], color='yellow', s=100, label='Sun')
        
        ax.set_xlabel('X (AU)')
        ax.set_ylabel('Y (AU)')
        ax.set_zlabel('Z (AU)')
        ax.set_title(f'3D Heliocentric Trajectory - {run_id}')
        ax.legend()
        
        plt.savefig(os.path.join(out_dir, 'trajectory_3d.png'))
        plt.close()

    def _plot_distance(self, df, run_id, out_dir):
        plt.figure(figsize=(10, 6))
        r = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
        # Convert to relevant units (e.g. AU or km). Assuming km from sim.
        r_au = r / 1.496e8 
        
        plt.plot(df['time'] / 86400, r_au, label='Heliocentric Distance')
        plt.xlabel('Time (days)')
        plt.ylabel('Distance (AU)')
        plt.title(f'Trajectory Evolution - {run_id}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'distance_vs_time.png'))
        plt.close()

    def _plot_energy(self, df, run_id, out_dir):
        if 'energy' not in df.columns:
            return
            
        plt.figure(figsize=(10, 6))
        plt.plot(df['time'] / 86400, df['energy'], color='orange')
        plt.xlabel('Time (days)')
        plt.ylabel('Specific Energy (km^2/s^2)')
        plt.title(f'Orbital Energy - {run_id}')
        plt.grid(True)
        plt.savefig(os.path.join(out_dir, 'energy_vs_time.png'))
        plt.close()

    def _plot_velocity(self, df, run_id, out_dir):
        v = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['time'] / 86400, v, color='green')
        plt.xlabel('Time (days)')
        plt.ylabel('Velocity (km/s)')
        plt.title(f'Velocity Profile - {run_id}')
        plt.grid(True)
        plt.savefig(os.path.join(out_dir, 'velocity_vs_time.png'))
        plt.close()

    def generate_campaign_summary(self):
        """Generates campaign-level scatter plots."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT sail_area, mass, final_energy, time_of_flight, escape_flag FROM campaign_runs"
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"DB Error: {e}")
            conn.close()
            return
        conn.close()
        
        if df.empty:
            print("No completed runs to plot.")
            return

        # 1. Area vs Mass colored by Energy
        plt.figure(figsize=(10, 6))
        # optimize marker size for large datasets
        marker_size = 20 if len(df) < 1000 else 2
        alpha = 0.6 if len(df) < 1000 else 0.3
        
        sc = plt.scatter(df['sail_area'], df['mass'], c=df['final_energy'], cmap='viridis', s=marker_size, alpha=alpha)
        plt.colorbar(sc, label='Final Energy')
        plt.xlabel('Sail Area (m^2)')
        plt.ylabel('Mass (kg)')
        plt.title('Design Space: Area vs Mass vs Energy')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, 'campaign_area_mass_energy.png'))
        plt.close()
        
        # 2. Escape Success
        plt.figure(figsize=(10, 6))
        escaped = df[df['escape_flag'] == 1]
        trapped = df[df['escape_flag'] == 0]
        
        plt.scatter(escaped['sail_area'], escaped['mass'], c='blue', label='Escaped', alpha=alpha, s=marker_size)
        plt.scatter(trapped['sail_area'], trapped['mass'], c='red', label='Trapped', alpha=alpha, s=marker_size)
        plt.xlabel('Sail Area (m^2)')
        plt.ylabel('Mass (kg)')
        plt.title('Escape Success Regions')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, 'campaign_escape_regions.png'))
        plt.close()

        # 3. Energy Distribution (Histogram)
        self._plot_energy_hist(df)

        # 4. 3D Design Space
        self._plot_design_space_3d(df)

    def _plot_energy_hist(self, df):
        plt.figure(figsize=(10, 6))
        plt.hist(df['final_energy'], bins=50, color='skyblue', edgecolor='black')
        plt.xlabel('Final Specific Energy (km^2/s^2)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Final Energy across Campaign')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.output_dir, 'campaign_energy_hist.png'))
        plt.close()

    def _plot_design_space_3d(self, df):
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        marker_size = 20 if len(df) < 1000 else 2
        alpha = 0.6 if len(df) < 1000 else 0.3
        
        sc = ax.scatter(df['sail_area'], df['mass'], df['final_energy'], c=df['final_energy'], cmap='viridis', s=marker_size, alpha=alpha)
        plt.colorbar(sc, label='Final Energy')
        
        ax.set_xlabel('Sail Area (m^2)')
        ax.set_ylabel('Mass (kg)')
        ax.set_zlabel('Final Energy')
        ax.set_title('3D Design Space Landscape')
        
        plt.savefig(os.path.join(self.output_dir, 'campaign_design_space_3d.png'))
        plt.close()
