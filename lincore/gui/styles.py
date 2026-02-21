NASA_STYLE = """
/* Main Window Background */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #252526;
}

QTabBar::tab {
    background: #2d2d30;
    color: #aaaaaa;
    padding: 8px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #007acc;
    color: #ffffff;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #444444;
    border-radius: 4px;
    margin-top: 20px; /* Leave space for title */
    color: #cccccc;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #00aaff;
}

/* Inputs */
QLineEdit, QDoubleSpinBox, QComboBox {
    background-color: #333333;
    border: 1px solid #555555;
    color: #ffffff;
    padding: 4px;
    border-radius: 2px;
}

QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #007acc;
}

/* Labels */
QLabel {
    color: #cccccc;
}

/* PushButton */
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #094770;
}

QPushButton:disabled {
    background-color: #3a3d41;
    color: #7f7f7f;
}

/* StatusBar */
QStatusBar {
    background-color: #007acc;
    color: white;
}

/* ProgressBar */
QProgressBar {
    border: 1px solid #333333;
    border-radius: 2px;
    text-align: center;
    background-color: #2d2d30;
    color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    width: 10px;
}
"""
