from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import os

class Visualization3D(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.browser = QWebEngineView()
        # Transparent background for browser widget itself
        self.browser.page().setBackgroundColor(self.palette().color(self.backgroundRole()))
        layout.addWidget(self.browser)
        self.setLayout(layout)
        
        # Initial empty plot
        self.plot_trajectory([])

    def plot_trajectory(self, history, config=None):
        """
        Plot 3D trajectory with NASA style.
        """
        fig = go.Figure()
        
        if not history:
            fig.update_layout(
                title="Waiting for Mission Data...",
                template="plotly_dark",
                 paper_bgcolor="#1e1e1e",
                 plot_bgcolor="#1e1e1e",
                scene = dict(
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )
        else:
            df = pd.DataFrame(history)
            
            # Identify Central Body
            body_name = 'Earth'
            body_color = '#2f80ed' # Blue
            body_size = 12
            
            if config:
                orbit_type = config.get('orbit', {}).get('type', 'LEO')
                if orbit_type == 'Heliocentric':
                    body_name = 'Sun'
                    body_color = '#ffaa00' # Yellow/Orange
                    body_size = 20
            
            # Central Body marker
            fig.add_trace(go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                marker=dict(size=body_size, color=body_color, line=dict(color='white', width=1)),
                name=body_name
            ))
            
            # Trajectory - Neon Cyan
            fig.add_trace(go.Scatter3d(
                x=df['rx'], y=df['ry'], z=df['rz'],
                mode='lines',
                line=dict(color='#00f0ff', width=3),
                name='Trajectory'
            ))
            
            # Start/End Markers
            fig.add_trace(go.Scatter3d(
                x=[df['rx'].iloc[0]], y=[df['ry'].iloc[0]], z=[df['rz'].iloc[0]],
                mode='markers', marker=dict(size=6, color='#4CAF50'), name='Start'
            ))
            fig.add_trace(go.Scatter3d(
                x=[df['rx'].iloc[-1]], y=[df['ry'].iloc[-1]], z=[df['rz'].iloc[-1]],
                mode='markers', marker=dict(size=6, color='#ff5555'), name='End'
            ))
            
            fig.update_layout(
                title=dict(text="3D Mission Trajectory", font=dict(color='#00aaff', size=18)),
                template="plotly_dark",
                paper_bgcolor="#1e1e1e",
                plot_bgcolor="#1e1e1e",
                margin=dict(l=0, r=0, b=0, t=40),
                scene=dict(
                    xaxis=dict(backgroundcolor="#1e1e1e", gridcolor="#333333", showbackground=True),
                    yaxis=dict(backgroundcolor="#1e1e1e", gridcolor="#333333", showbackground=True),
                    zaxis=dict(backgroundcolor="#1e1e1e", gridcolor="#333333", showbackground=True),
                    aspectmode='data'
                ),
                legend=dict(font=dict(color="#cccccc"))
            )

        html = pio.to_html(fig, include_plotlyjs='cdn')
        self.browser.setHtml(html)
