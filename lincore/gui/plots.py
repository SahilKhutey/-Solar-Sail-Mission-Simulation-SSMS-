from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
import numpy as np

from lincore.forces.gravity import MU_EARTH
from lincore.environment.ephemeris import MU_SUN
from lincore.analysis.orbital_elements import state_to_keplerian


class PlotsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Sub-tabs for Plots
        self.tabs = QTabWidget()

        self.elements_browser = QWebEngineView()
        self.diagnostics_browser = QWebEngineView()

        # Transparent BG
        self.elements_browser.page().setBackgroundColor(self.palette().color(self.backgroundRole()))
        self.diagnostics_browser.page().setBackgroundColor(
            self.palette().color(self.backgroundRole())
        )

        self.tabs.addTab(self.elements_browser, "Elements")
        self.tabs.addTab(self.diagnostics_browser, "Diagnostics")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.plot_data([])

    def plot_data(self, history, config=None):
        if not history:
            self._show_empty(self.elements_browser)
            self._show_empty(self.diagnostics_browser)
            return

        df = pd.DataFrame(history)
        t_days = df["t"] / 86400.0

        # Determine Mu
        mu = MU_EARTH
        if config:
            orbit_type = config.get("orbit", {}).get("type", "LEO")
            if orbit_type == "Heliocentric":
                mu = MU_SUN

        # Vectorized calculation using numpy for speed over loop
        r_vec = df[["rx", "ry", "rz"]].values
        v_vec = df[["vx", "vy", "vz"]].values
        r_mag = np.linalg.norm(r_vec, axis=1)
        v_mag = np.linalg.norm(v_vec, axis=1)

        # Specific Energy
        eps = v_mag**2 / 2 - mu / r_mag

        # Angular Momentum
        h_vec = np.cross(r_vec, v_vec)
        h = np.linalg.norm(h_vec, axis=1)

        # SMA
        with np.errstate(divide="ignore"):
            a = -mu / (2 * eps)

        # Eccentricity
        e = np.sqrt(1 + 2 * eps * h**2 / mu**2)

        # Inclination
        with np.errstate(invalid="ignore"):
            i_rad = np.arccos(h_vec[:, 2] / h)
        i_deg = np.degrees(i_rad)

        # --- Plot 1: Orbital Elements ---
        fig1 = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Semi-major Axis (km/AU)",
                "Eccentricity",
                "Inclination (deg)",
                "Altitude/Dist",
            ),
        )

        # Check scale for SMA (km vs AU)
        if mu == MU_SUN:
            a_plot = a / 1.496e8
            dist_plot = r_mag / 1.496e8
            lbl_a = "SMA (AU)"
            lbl_dist = "Dist (AU)"
        else:
            a_plot = a
            dist_plot = r_mag - 6378.0
            lbl_a = "SMA (km)"
            lbl_dist = "Alt (km)"

        fig1.add_trace(
            go.Scatter(x=t_days, y=a_plot, name=lbl_a, line=dict(color="#00aaff")), row=1, col=1
        )
        fig1.add_trace(
            go.Scatter(x=t_days, y=e, name="Ecc", line=dict(color="#ffaa00")), row=1, col=2
        )
        fig1.add_trace(
            go.Scatter(x=t_days, y=i_deg, name="Inc", line=dict(color="#00ffaa")), row=2, col=1
        )
        fig1.add_trace(
            go.Scatter(x=t_days, y=dist_plot, name=lbl_dist, line=dict(color="#ff5555")),
            row=2,
            col=2,
        )

        self._apply_theme(fig1)
        self.elements_browser.setHtml(pio.to_html(fig1, include_plotlyjs="cdn"))

        # --- Plot 2: Diagnostics ---
        fig2 = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Specific Energy",
                "Angular Momentum",
                "Hamiltonian Error (Drift)",
                "Eclipse Flag",
            ),
        )

        fig2.add_trace(
            go.Scatter(x=t_days, y=eps, name="Energy", line=dict(color="#ff5555")), row=1, col=1
        )
        fig2.add_trace(
            go.Scatter(x=t_days, y=h, name="Ang Mom", line=dict(color="#00aaff")), row=1, col=2
        )

        # Drift (Relative to initial)
        d_eps = (eps - eps[0]) / abs(eps[0]) if abs(eps[0]) > 1e-9 else eps
        fig2.add_trace(
            go.Scatter(x=t_days, y=d_eps, name="Energy Drift", line=dict(color="#ffff00")),
            row=2,
            col=1,
        )

        # Eclipse (Placeholder for now, need in history)
        # For now, just plot zero
        fig2.add_trace(
            go.Scatter(
                x=t_days, y=np.zeros_like(t_days), name="Eclipse", line=dict(color="#888888")
            ),
            row=2,
            col=2,
        )

        self._apply_theme(fig2)
        self.diagnostics_browser.setHtml(pio.to_html(fig2, include_plotlyjs="cdn"))

    def _apply_theme(self, fig):
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1e1e1e",
            plot_bgcolor="#252526",
            font=dict(color="#e0e0e0"),
            margin=dict(l=50, r=20, t=50, b=50),
            height=600,
            showlegend=False,
        )

    def _show_empty(self, browser):
        fig = go.Figure()
        fig.update_layout(
            title="No Data", template="plotly_dark", paper_bgcolor="#1e1e1e", plot_bgcolor="#1e1e1e"
        )
        browser.setHtml(pio.to_html(fig, include_plotlyjs="cdn"))
