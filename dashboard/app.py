
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import pickle
import os
import numpy as np

# Page Config
st.set_page_config(
    page_title="Solar Sail Research Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
DB_PATH = "research_database/mission_data.db"
MODEL_PATH = "analysis/models/surrogate_energy.pkl"
TRAJ_PATH = "reports/Optimization/Verification_Run/manual_run/trajectory.parquet"

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

def set_space_theme(fig, title=""):
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis=dict(showgrid=True, gridcolor='#333333', zerolinecolor='#666666', showbackground=False, title='X (km)'),
            yaxis=dict(showgrid=True, gridcolor='#333333', zerolinecolor='#666666', showbackground=False, title='Y (km)'),
            zaxis=dict(showgrid=True, gridcolor='#333333', zerolinecolor='#666666', showbackground=False, title='Z (km)'),
            bgcolor='#050510' # Deep space blue-black
        ),
        paper_bgcolor='#0E1117',
        plot_bgcolor='#0E1117',
        font=dict(family="Arial, sans-serif", color='#E0E0E0'),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig


@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT run_id, sail_area, mass, reflectivity, thickness, launch_altitude, 
           final_energy, min_distance_sun, escape_flag
    FROM campaign_runs
    WHERE final_energy IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Campaign Explorer", "Surrogate Model", "Sensitivity Analysis", "3D Visualization", "Optimal Design", "Mission Designer (Custom)", "Research Report"])

# Load Data
df = load_data()
model = load_model()

if page == "Campaign Explorer":
    st.title("🛰️ Design Space Explorer")
    st.markdown(f"**Total Runs:** {len(df)}")
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("X Axis", df.columns, index=1)
    with col2:
        y_axis = st.selectbox("Y Axis", df.columns, index=6) # final_energy
        
    c_axis = st.selectbox("Color By", df.columns, index=2)
    
    # Cap plotting points to prevent browser freeze
    plot_df = df
    if len(plot_df) > 5000:
        plot_df = plot_df.sample(5000, random_state=42)
        st.warning("Scatter plot downsampled to 5,000 points for performance.")
    
    fig = px.scatter(plot_df, x=x_axis, y=y_axis, color=c_axis, 
                     hover_data=['run_id'], title=f"<b>{y_axis}</b> vs <b>{x_axis}</b>",
                     color_continuous_scale=px.colors.sequential.Viridis,
                     template="plotly_dark")
    fig.update_traces(marker=dict(size=6, opacity=0.8, line=dict(width=0.5, color='white')))
    fig.update_layout(title_x=0.5, font=dict(family="Arial, sans-serif", size=12, color="lightgray"),
                      paper_bgcolor='#0E1117', plot_bgcolor='#0E1117')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df)

elif page == "Surrogate Model":
    st.title("🧠 AI Predictor")
    st.markdown("Predict outcomes for new designs instantly using the trained Gradient Boosting model.")
    
    if model:
        st.subheader("Design Parameters")
        c1, c2, c3 = st.columns(3)
        area = c1.number_input("Sail Area (m²)", 1000.0, 100000.0, 91000.0)
        mass = c2.number_input("Mass (kg)", 10.0, 500.0, 308.0)
        alt = c3.number_input("Altitude (km)", 400.0, 50000.0, 35740.0)
        
        c4, c5 = st.columns(2)
        refl = c4.slider("Reflectivity", 0.7, 1.0, 0.9)
        thick = c5.slider("Thickness (um)", 1.0, 10.0, 2.0)
        
        # Predict
        # Input DataFrame must match training cols: 
        # ['sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude']
        input_data = pd.DataFrame([[area, mass, refl, thick, alt]], 
                                  columns=['sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude'])
        
        if st.button("Predict Performance"):
            pred_energy = model.predict(input_data)[0]
            st.metric("Predicted Energy (J/kg)", f"{pred_energy:.4f}")
            
            if pred_energy > 0:
                st.success("🚀 ESCAPE TRAJECTORY PREDICTED")
            else:
                st.warning("⚠️ BOUND ORBIT PREDICTED")
    else:
        st.error("Model not found. Train usage 'train_surrogate.py' first.")

elif page == "3D Visualization":
    st.title("🌌 Trajectory Viewer")
    st.write("Visualizing the 'Theoretical Optimal' trajectory (Run Verification).")
    
    if os.path.exists(TRAJ_PATH):
        traj_df = pd.read_parquet(TRAJ_PATH)
        # Downsample
        if len(traj_df) > 2000:
            traj_df = traj_df.iloc[::len(traj_df)//2000]
            
        fig = go.Figure()
        # Sun
        fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=15, color='yellow'), name='Sun'))
        # Path
        fig.add_trace(go.Scatter3d(x=traj_df['x'], y=traj_df['y'], z=traj_df['z'], mode='lines', line=dict(color='cyan', width=3), name='Sail'))
        # Start/End
        fig.add_trace(go.Scatter3d(x=[traj_df.iloc[0]['x']], y=[traj_df.iloc[0]['y']], z=[traj_df.iloc[0]['z']], mode='markers', marker=dict(size=5, color='green'), name='Start'))
        fig.add_trace(go.Scatter3d(x=[traj_df.iloc[-1]['x']], y=[traj_df.iloc[-1]['y']], z=[traj_df.iloc[-1]['z']], mode='markers', marker=dict(size=5, color='red'), name='End'))
        
        fig = set_space_theme(fig, "Optimal Solar Sail Earth Escape Trajectory")
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Journey file not found.")

elif page == "Optimal Design":
    st.title("🏆 Theoretical Limits")
    st.write("According to Differential Evolution:")
    st.code("""
    Optimal Configuration:
      Sail Area: 91,029 m²
      Mass: 308 kg
      Reflectivity: ~0.80
      Thickness: ~3.2 um
      Launch Altitude: 35,740 km (GEO)
      
    Predicted Outcome:
      Final Energy: -4.72 J/kg (Max Safe)
    """)
    st.info("Note: True Solar System Escape requires >> 10 years or closer solar approach. This design maximizes energy within the 100-day safety constraints.")

elif page == "Mission Designer (Custom)":
    st.title("🛠️ Custom Mission Designer")
    st.markdown("Configure and run a physics simulation directly from the browser.")
    
    with st.form("simulation_form"):
        c1, c2 = st.columns(2)
        c1.subheader("Spacecraft")
        area = c1.number_input("Sail Area (m²)", 100.0, 200000.0, 91000.0)
        mass = c1.number_input("Mass (kg)", 1.0, 1000.0, 308.0)
        refl = c1.slider("Reflectivity", 0.5, 1.0, 0.9)
        
        c2.subheader("Orbit & Mission")
        target = c2.selectbox("Target Destination", ["None", "Moon", "Mars", "Venus", "Sun"])
        alt = c2.number_input("Altitude (km)", 200.0, 100000.0, 35740.0)
        duration = c2.slider("Duration (Days)", 1, 1000, 100)
        
        submitted = st.form_submit_button("🚀 Run Simulation")
        
    if submitted:
        import subprocess
        import sys
        import yaml
        
        # 1. Create Config
        custom_config = {
            'mission': {'name': 'Custom User Run', 'duration_days': float(duration), 'step_size': 60.0},
            'spacecraft': {'sail_area': area, 'mass': mass, 'reflectivity': refl, 'thickness': 2.0, 
                           'cd': 2.2, 'inertia': [[100,0,0],[0,100,0],[0,0,100]], 'r_cp': [0,0,0]},
            'orbit': {'type': 'LEO', 'altitude_km': alt, 'inclination_deg': 28.5, 'eccentricity': 0.001},
            'physics': {'integrator': 'rk45', 'perturbations': {'J2': True, 'drag': False, 'n_body': ['SUN', 'MOON']}, 'gravity_model': 'two_body'},
            'output': {'log_file': 'mission_log.csv', 'log_interval': 300.0},
            'navigation': {'position_noise_km': 0.0, 'velocity_noise_kms': 0.0, 'attitude_noise_deg': 0.0, 'rate_noise_deg_s': 0.0}
        }
        
        # 2. Save Config
        os.makedirs("temp/custom_run", exist_ok=True)
        config_path = "temp/custom_run/config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)
            
        # 3. Run Runner
        cmd = [sys.executable, "mission_campaign/runner.py", config_path, "--output_dir", "temp/custom_run", "--run_id", "user_sim"]
        
        with st.spinner(f"Running physics engine for {duration} days..."):
            try:
                process = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if process.returncode == 0:
                    st.success("Simulation Complete!")
                else:
                    st.error(f"Simulation Failed with code {process.returncode}.")
                    st.error(f"STDOUT: {process.stdout}")
                    st.error(f"STDERR: {process.stderr}")
            except Exception as e:
                process = None
                st.error(f"Failed to launch subprocess: {str(e)}")
            
        if process and process.returncode == 0:
            # 4. Visualize
            traj_file = "temp/custom_run/user_sim/trajectory.parquet"
            if os.path.exists(traj_file):
                df = pd.read_parquet(traj_file)
                st.metric("Final Dist from Earth (km)", f"{np.linalg.norm(df.iloc[-1][['x','y','z']]):.2f}")
                
                 # Downsample
                if len(df) > 2000:
                    df = df.iloc[::len(df)//2000]

                fig = go.Figure()
                # Earth (Center)
                fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=20, color='blue'), name='Earth'))
                
                # Target Logic Use Ephemeris
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                from lincore.environment.ephemeris import get_body_state
                
                # Restore approximate targets for reference lines
                targets = {
                    "Moon":  {"dist": 384400, "color": "gray"},
                    "Mars":  {"dist": 78000000, "color": "red"}, 
                    "Venus": {"dist": 40000000, "color": "orange"},
                    "Sun":   {"dist": 149600000, "color": "yellow"}
                }
                
                from lincore.environment.ephemeris import get_body_state
                
                if target != "None" and target != "Sun":
                    # Get final time
                    t_end_sec = df.iloc[-1]['time']
                    
                    # Get target state at t_end (Heliocentric)
                    try:
                        r_target_helio = get_body_state(target.lower(), t_end_sec)[:3]
                        r_earth_helio = get_body_state('earth', t_end_sec)[:3]
                        
                        # Target relative to Earth
                        r_target_geo = r_target_helio - r_earth_helio
                        dist_real = np.linalg.norm(r_target_geo)
                        
                        # Plot Real Target
                        fig.add_trace(go.Scatter3d(x=[r_target_geo[0]], y=[r_target_geo[1]], z=[r_target_geo[2]], 
                                                   mode='markers+text', marker=dict(size=15, color='red'), 
                                                   name=f"{target} (Actual)", text=[target]))
                                                   
                        # Add Line to Target?
                        # fig.add_trace(go.Scatter3d(x=[0, r_target_geo[0]], y=[0, r_target_geo[1]], z=[0, r_target_geo[2]],
                        #                            mode='lines', line=dict(color='gray', dash='dash'), name='Line of Sight'))
                        
                        st.caption(f"Actual Distance to {target}: {dist_real:,.0f} km")
                        
                    except Exception as e:
                        st.warning(f"Could not load ephemeris for {target}: {e}")
                elif target == "Sun":
                     fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=30, color='yellow'), name='Sun (Far Away)'))
                
                # Path
                fig.add_trace(go.Scatter3d(x=df['x'], y=df['y'], z=df['z'], mode='lines', line=dict(color='cyan', width=4), name='Sail Trajectory'))
                fig.add_trace(go.Scatter3d(x=[df.iloc[0]['x']], y=[df.iloc[0]['y']], z=[df.iloc[0]['z']], mode='markers', marker=dict(size=5, color='green'), name='Start'))
                fig.add_trace(go.Scatter3d(x=[df.iloc[-1]['x']], y=[df.iloc[-1]['y']], z=[df.iloc[-1]['z']], mode='markers', marker=dict(size=5, color='red'), name='End'))
                
                fig = set_space_theme(fig, "Custom Mission Trajectory")
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)

                # 5. 2D Telemetry
                st.subheader("📊 Telemetry Analysis")
                df['velocity'] = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
                df['distance_earth'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2) # Corrected label
                df['days'] = df['time'] / 86400.0
                
                c1, c2 = st.columns(2)
                
                with c1:
                    st.write("**Velocity vs Time**")
                    fig_vel = px.line(df, x='days', y='velocity', title='Velocity (km/s)', template='plotly_dark')
                    fig_vel.update_traces(line=dict(color='#00FFCC', width=2))
                    fig_vel.update_layout(paper_bgcolor='#0E1117', plot_bgcolor='#0E1117')
                    st.plotly_chart(fig_vel, use_container_width=True)
                    
                with c2:
                    st.write("**Distance from Earth vs Time**")
                    fig_dist = px.line(df, x='days', y='distance_earth', title='Distance (km)', template='plotly_dark')
                    fig_dist.update_traces(line=dict(color='#FF00CC', width=2))
                    fig_dist.update_layout(paper_bgcolor='#0E1117', plot_bgcolor='#0E1117')
                    # Add Target Line
                    if target in targets:
                         fig_dist.add_hline(y=targets[target]["dist"], line_dash="dash", line_color="red", annotation_text=f"Orbit of {target}")
                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.error("Trajectory file missing.")
        else:
            st.error("Simulation Failed.")
            st.code(process.stderr)

elif page == "Sensitivity Analysis":
    st.title("🌪️ Sensitivity Analysis")
    st.markdown("Quantifying which design parameters impact the mission success the most.")
    
    img_path = "reports/Sensitivity/feature_importance.png"
    if os.path.exists(img_path):
        st.image(img_path, caption="Feature Importance (Gradient Boosting Model)", use_container_width=True)
    else:
        st.warning("Feature importance plot not found. Run 'analysis/sensitivity.py'.")
        
    st.info("Top Factor: **Sail Area** (Controls solar radiation pressure force).")

elif page == "Research Report":
    st.title("📄 Research Findings")
    report_path = "reports/Research_Findings/Research_Summary.md"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
        st.markdown(content)
    else:
        st.error("Report not found. Run 'analysis/compile_research_report.py'.")
