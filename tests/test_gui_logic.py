import sys
import os

# Add project root (parent of tests/) to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from PyQt6.QtWidgets import QApplication
    from lincore.gui.plots import PlotsPanel
    from lincore.gui.visualization_3d import Visualization3D

    HAS_QT = True
except ImportError:
    HAS_QT = False
    print("PyQt6 not found. Skipping GUI-widget tests.")

from lincore.mission.controller import MissionController

# Global app instance for Qt tests
app_instance = None


def get_app():
    global app_instance
    if not HAS_QT:
        return None
    if app_instance is None:
        if QApplication.instance():
            app_instance = QApplication.instance()
        else:
            app_instance = QApplication(sys.argv)
    return app_instance


def test_controller_leo():
    """Test MissionController with LEO config."""
    print("Testing Controller (LEO)...")
    controller = MissionController()
    config = {
        "mission": {"duration_days": 0.01, "step_size": 60.0},  # Short run
        "spacecraft": {
            "mass": 10,
            "sail_area": 100,
            "reflectivity": 0.9,
            "inertia": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        },
        "orbit": {"type": "LEO", "altitude_km": 700.0, "inclination_deg": 28.5},
        "physics": {"gravity_model": "two_body", "perturbations": {}, "navigation": False},
        "output": {"log_file": "test_gui.csv"},
    }

    # Run
    history = controller.run_mission(config)
    assert len(history) > 0
    assert "rx" in history[0]
    print("Controller LEO Passed.")


def test_plot_logic_leo():
    """Test PlotsPanel logic with LEO data."""
    if not HAS_QT:
        return
    print("Testing Plots Logic (LEO)...")
    app = get_app()
    panel = PlotsPanel()

    # Mock data
    history = [
        {"t": 0, "rx": 7000, "ry": 0, "rz": 0, "vx": 0, "vy": 7.5, "vz": 0},
        {"t": 60, "rx": 7000, "ry": 450, "rz": 0, "vx": -0.5, "vy": 7.5, "vz": 0},
    ]
    config = {"orbit": {"type": "LEO"}}

    # Should not raise exception
    panel.plot_data(history, config)
    print("Plots LEO Passed.")


def test_plot_logic_helio():
    """Test PlotsPanel logic with Heliocentric data."""
    if not HAS_QT:
        return
    print("Testing Plots Logic (Heliocentric)...")
    app = get_app()
    panel = PlotsPanel()

    # Mock data (1 AU)
    au = 1.496e8
    history = [
        {"t": 0, "rx": au, "ry": 0, "rz": 0, "vx": 0, "vy": 29.78, "vz": 0},
        {"t": 60, "rx": au, "ry": 1786, "rz": 0, "vx": -0.1, "vy": 29.78, "vz": 0},
    ]
    config = {"orbit": {"type": "Heliocentric"}}

    # Should not raise exception
    panel.plot_data(history, config)
    print("Plots Heliocentric Passed.")


def test_viz_logic():
    """Test Visualization3D logic."""
    if not HAS_QT:
        return
    print("Testing Viz Logic...")
    app = get_app()
    viz = Visualization3D()

    history = [{"t": 0, "rx": 7000, "ry": 0, "rz": 0, "vx": 0, "vy": 7.5, "vz": 0}]
    config = {"orbit": {"type": "LEO"}}

    viz.plot_trajectory(history, config)
    print("Viz Logic Passed.")


if __name__ == "__main__":
    # If run directly
    test_controller_leo()
    test_plot_logic_leo()
    test_plot_logic_helio()
    test_viz_logic()
    print("ALL GUI LOGIC TESTS PASSED.")
