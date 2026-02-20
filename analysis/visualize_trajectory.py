
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

INPUT_FILE = "reports/Optimization/Verification_Run/manual_run/trajectory.parquet"
OUTPUT_DIR = "reports/Optimization"

def plot_trajectory():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    df = pd.read_parquet(INPUT_FILE)
    
    # Downsample for performance if needed
    if len(df) > 5000:
        df = df.iloc[::len(df)//5000]
        
    # Create 3D Plot
    fig = go.Figure()
    
    # Sun
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='yellow', symbol='circle'),
        name='Sun'
    ))
    
    # Trajectory
    fig.add_trace(go.Scatter3d(
        x=df['x'], y=df['y'], z=df['z'],
        mode='lines',
        line=dict(color='cyan', width=2),
        name='Solar Sail Trajectory'
    ))
    
    # Start Point
    fig.add_trace(go.Scatter3d(
        x=[df.iloc[0]['x']], y=[df.iloc[0]['y']], z=[df.iloc[0]['z']],
        mode='markers',
        marker=dict(size=5, color='green'),
        name='Start'
    ))
    
    # End Point
    fig.add_trace(go.Scatter3d(
        x=[df.iloc[-1]['x']], y=[df.iloc[-1]['y']], z=[df.iloc[-1]['z']],
        mode='markers',
        marker=dict(size=5, color='red'),
        name='End'
    ))
    
    # Layout with Dark Theme
    fig.update_layout(
        title="Optimal Solar Sail Trajectory (100 Days)",
        scene=dict(
            xaxis_title='X (km)',
            yaxis_title='Y (km)',
            zaxis_title='Z (km)',
            aspectmode='data',
            bgcolor='rgb(20, 20, 20)'
        ),
        paper_bgcolor='rgb(20, 20, 20)',
        font=dict(color='white')
    )
    
    output_path = os.path.join(OUTPUT_DIR, "optimal_trajectory_3d.html")
    fig.write_html(output_path)
    print(f"3D Plot saved to {output_path}")
    
    # Also save static image for report if psutil is installed (kaleido needed usually)
    # plain write_image might fail without dependencies, skipping for now.

if __name__ == "__main__":
    plot_trajectory()
