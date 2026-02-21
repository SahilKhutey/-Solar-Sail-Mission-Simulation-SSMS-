import plotly.graph_objects as go
import numpy as np
from lincore.environment.ephemeris import AU


def plot_trajectory_3d(history):
    """
    Plot 3D trajectory of spacecraft.
    history: dict or dataframe with t, r_x, r_y, r_z
    """
    fig = go.Figure()

    # Extract data
    x = history["rx"]
    y = history["ry"]
    z = history["rz"]

    # Sun
    fig.add_trace(
        go.Scatter3d(
            x=[0], y=[0], z=[0], mode="markers", marker=dict(size=10, color="yellow"), name="Sun"
        )
    )

    # Spacecraft Path
    fig.add_trace(
        go.Scatter3d(
            x=x, y=y, z=z, mode="lines", line=dict(color="blue", width=4), name="Solar Sail"
        )
    )

    # Start/End
    fig.add_trace(
        go.Scatter3d(
            x=[x[0]],
            y=[y[0]],
            z=[z[0]],
            mode="markers",
            marker=dict(size=5, color="green"),
            name="Start",
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[x[-1]],
            y=[y[-1]],
            z=[z[-1]],
            mode="markers",
            marker=dict(size=5, color="red"),
            name="End",
        )
    )

    fig.update_layout(
        title="3D Mission Trajectory",
        scene=dict(
            xaxis_title="X (km)", yaxis_title="Y (km)", zaxis_title="Z (km)", aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    return fig


def plot_attitude_sphere(n_history):
    """
    Visualize sail normal vector evolution on a unit sphere.
    """
    fig = go.Figure()

    # Unit Sphere Wireframe
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 10)
    # Using simple meshgrid for wireframe
    nx = np.outer(np.cos(u), np.sin(v))
    ny = np.outer(np.sin(u), np.sin(v))
    nz = np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(go.Surface(x=nx, y=ny, z=nz, opacity=0.1, showscale=False))

    # Normal Vectors (as list of vectors)
    px = [v[0] for v in n_history]
    py = [v[1] for v in n_history]
    pz = [v[2] for v in n_history]

    fig.add_trace(
        go.Scatter3d(
            x=px,
            y=py,
            z=pz,
            mode="lines+markers",
            marker=dict(size=3, color="purple"),
            line=dict(color="purple", width=2),
            name="Sail Normal",
        )
    )

    fig.update_layout(
        title="Attitude Evolution (Body Normal)",
        scene=dict(
            xaxis=dict(range=[-1, 1]),
            yaxis=dict(range=[-1, 1]),
            zaxis=dict(range=[-1, 1]),
            aspectmode="cube",
        ),
    )

    return fig
