import sys
import os

# Add project root to path
sys.path.append(os.path.abspath('.'))

from PyQt6.QtWidgets import QApplication
from lincore.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
