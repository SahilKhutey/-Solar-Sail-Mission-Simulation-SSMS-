from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame

class TelemetryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Grid for metrics
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Labels
        self.vel_val = self.create_metric(grid, "VELOCITY", "0.000", "km/s", 0, 0)
        self.alt_val = self.create_metric(grid, "ALTITUDE", "0.0", "km", 0, 1)
        self.dist_val = self.create_metric(grid, "SUN DIST", "0.000", "AU", 1, 0)
        self.srp_val = self.create_metric(grid, "SRP ACC", "0.000", "mm/s²", 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
        self.setLayout(layout)
        
    def create_metric(self, grid, title, default, unit, row, col):
        frame = QFrame()
        frame.setStyleSheet("background-color: #252526; border: 1px solid #333; border-radius: 4px;")
        vbox = QVBoxLayout()
        vbox.setContentsMargins(10, 5, 10, 5)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        
        lbl_val = QLabel(default)
        lbl_val.setStyleSheet("color: #00f0ff; font-size: 18px; font-family: monospace;")
        
        lbl_unit = QLabel(unit)
        lbl_unit.setStyleSheet("color: #666; font-size: 10px;")
        
        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        vbox.addWidget(lbl_unit)
        frame.setLayout(vbox)
        grid.addWidget(frame, row, col)
        
        return lbl_val

    def update_telemetry(self, state):
        # state: {'t', 'rx', 'ry', 'rz', 'vx', 'vy', 'vz'}
        import numpy as np
        
        r = np.array([state['rx'], state['ry'], state['rz']])
        v = np.array([state['vx'], state['vy'], state['vz']])
        
        # Velocity
        v_mag = np.linalg.norm(v)
        self.vel_val.setText(f"{v_mag:.3f}")
        
        # Distance (AU)
        r_mag_km = np.linalg.norm(r)
        r_au = r_mag_km / 1.496e8
        self.dist_val.setText(f"{r_au:.4f}")
        
        # Altitude (assuming Earth centered for now, or just R mag)
        # If LEO, subtract Earth Radius
        R_EARTH = 6378.0
        alt = r_mag_km - R_EARTH
        if alt > 0:
            self.alt_val.setText(f"{alt:.1f}")
        else:
            self.alt_val.setText("N/A")
            
        # SRP Acceleration (Approximation for display)
        # Acc ~ 1/r^2
        # roughly P * A/m * (1/r_au)^2
        # Just show placeholder or calc if mass available?
        # For now, just show 1/r^2 sort of scaling relative to 1AU
        srp_scale = 1.0 / (r_au**2) if r_au > 0 else 0
        self.srp_val.setText(f"{srp_scale:.2f} x")
