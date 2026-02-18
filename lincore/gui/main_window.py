from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTabWidget, QStatusBar, QProgressBar, QMessageBox, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt

from lincore.gui.config_panel import ConfigPanel
from lincore.gui.visualization_3d import Visualization3D
from lincore.gui.plots import PlotsPanel
from lincore.gui.telemetry_panel import TelemetryPanel
from lincore.mission.controller import MissionController
from lincore.gui.styles import NASA_STYLE

class SimulationThread(QThread):
    progress_signal = pyqtSignal(float, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, controller, config):
        super().__init__()
        self.controller = controller
        self.config = config
        
    def run(self):
        try:
            history = self.controller.run_mission(
                self.config, 
                callback=self.callback
            )
            self.finished_signal.emit(history)
        except Exception as e:
            self.error_signal.emit(str(e))
            
    def callback(self, progress, status):
        self.progress_signal.emit(progress, status)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solar Sail Mission Control - Lincore v1.0")
        self.resize(1600, 900)
        
        # Apply Theme
        self.setStyleSheet(NASA_STYLE)
        
        self.controller = MissionController()
        self.sim_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Splitter (Left vs Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Config & Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        self.config_panel = ConfigPanel()
        left_layout.addWidget(self.config_panel)
        
        # Telemetry Panel
        self.telemetry = TelemetryPanel()
        left_layout.addWidget(self.telemetry)
        
        # Run Button
        self.run_btn = QPushButton("INITIATE TRAJECTORY")
        self.run_btn.setStyleSheet("font-size: 14px; padding: 12px; background-color: #0e639c;")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self.start_simulation)
        left_layout.addWidget(self.run_btn)
        
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right Panel: Tabs (3D Viz, Plots, Telemetry)
        self.tabs = QTabWidget()
        self.viz_3d = Visualization3D()
        self.plots = PlotsPanel()
        
        self.tabs.addTab(self.viz_3d, "3D TRAJECTORY")
        self.tabs.addTab(self.plots, "ORBITAL ELEMENTS")
        
        # Add to Splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(self.tabs)
        
        splitter.setStretchFactor(1, 4) # Make right side larger
        
        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.showMessage("SYSTEM READY.")
        
    def start_simulation(self):
        config = self.config_panel.get_config()
        
        # Basic validation
        valid, msg = self.controller.validate_config(config)
        if not valid:
            QMessageBox.warning(self, "Configuration Error", msg)
            return
            
        # Disable UI
        self.run_btn.setEnabled(False)
        self.run_btn.setText("SIMULATION IN PROGRESS...")
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("CALCULATING TRAJECTORY...")
        
        # Start Thread
        self.sim_thread = SimulationThread(self.controller, config)
        self.sim_thread.progress_signal.connect(self.update_progress)
        self.sim_thread.finished_signal.connect(self.on_finished)
        self.sim_thread.error_signal.connect(self.on_error)
        self.sim_thread.start()
        
    def update_progress(self, val, msg):
        self.progress_bar.setValue(int(val * 100))
        self.status_bar.showMessage(msg.upper())
        
    def on_finished(self, history):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("INITIATE TRAJECTORY")
        self.status_bar.showMessage("MISSION COMPLETE. DATA READY.")
        self.progress_bar.setValue(100)
        
        # Use config from thread or panel
        config = self.sim_thread.config if self.sim_thread else None
        
        # Plot
        self.viz_3d.plot_trajectory(history, config=config)
        self.plots.plot_data(history, config=config)
        
        # Update Telemetry (Final State)
        if history:
            self.telemetry.update_telemetry(history[-1])
        
    def on_error(self, msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("INITIATE TRAJECTORY")
        self.status_bar.showMessage("SIMULATION FAILED.")
        QMessageBox.critical(self, "Runtime Error", msg)
