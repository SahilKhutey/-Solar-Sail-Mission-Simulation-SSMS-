import streamlit as st
import sys
import os
import numpy as np
import pandas as pd

# Add parent path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lincore.mission.pipeline import SolarSailMission
from lincore.ui.visualizer import plot_trajectory_3d

st.set_page_config(page_title="Solar Sail Mission Control", layout="wide")

st.title("🚀 Solar Sail Mission Control")

# Sidebar: Mission Configuration
st.sidebar.header("Mission Parameters")

# Initial Orbit
st.sidebar.subheader("Initial State")
orbit_type = st.sidebar.selectbox("Orbit Type", ["LEO (Earth)", "Heliocentric Cruise"])

if orbit_type == "LEO (Earth)":
    alt = st.sidebar.number_input("Altitude (km)", value=700.0)
    inc = st.sidebar.number_input("Inclination (deg)", value=28.5)
    orbit_config = {"type": "LEO", "altitude_km": alt, "inclination_deg": inc}
else:
    dist_au = st.sidebar.number_input("Distance (AU)", value=1.0)
    orbit_config = {"type": "Heliocentric", "distance_au": dist_au}

# Sail Properties
st.sidebar.subheader("Spacecraft Design")
area = st.sidebar.number_input("Sail Area (m^2)", value=100.0)
mass = st.sidebar.number_input("Total Mass (kg)", value=10.0)
reflectivity = st.sidebar.slider("Reflectivity", 0.0, 1.0, 0.9)

# Simulation Controls
st.sidebar.subheader("Simulation")
duration_days = st.sidebar.number_input("Duration (Days)", value=10.0)  # Increased default
step_size = st.sidebar.number_input("Step Size (s)", value=60.0)
integrator = st.sidebar.selectbox("Integrator", ["RK45", "Symplectic (Verlet)"])

# Config Construction
config = {
    "mission": {"start_date": "2026-01-01", "duration_days": duration_days, "step_size": step_size},
    "spacecraft": {
        "mass": mass,
        "sail_area": area,
        "reflectivity": reflectivity,
        "inertia": [[10, 0, 0], [0, 10, 0], [0, 0, 10]],  # Simplified
    },
    "orbit": orbit_config,
    "physics": {
        "gravity_model": "multi_body",
        "perturbations": {"j2": True, "srp": True, "drag": True},
        "integrator": "symplectic" if integrator == "Symplectic (Verlet)" else "rk45",
        "navigation": True,  # Enable EKF
    },
    "output": {"log_file": "gui_mission.csv"},
}

if st.sidebar.button("Run Mission"):
    st.info(f"Simulating {orbit_type} for {duration_days} days...")

    # Run Simulation
    mission = SolarSailMission(config)

    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = int(duration_days * 86400 / step_size)
    history = []

    # Subsample for plotting to avoid memory kill
    plot_interval = max(1, steps // 1000)

    for i in range(steps):
        t, state = mission.step()

        if i % plot_interval == 0:
            # Store [rx, ry, rz]
            history.append({"t": t, "rx": state[0], "ry": state[1], "rz": state[2]})

        if i % 100 == 0:
            progress_bar.progress(min(i / steps, 1.0))
            status_text.text(f"Simulating Day {t/86400:.2f}...")

    progress_bar.progress(1.0)
    status_text.text("Simulation Complete")

    st.success("Mission Successful")

    # Visualization
    st.subheader("Trajectory Analysis")

    df = pd.DataFrame(history)
    fig = plot_trajectory_3d(df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mission Data")
    st.dataframe(df.head())
