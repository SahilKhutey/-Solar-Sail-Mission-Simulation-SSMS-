from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, 
    QComboBox, QGroupBox, QLabel, QDoubleSpinBox
)

class ConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 1. Spacecraft Parameters
        sc_group = QGroupBox("Spacecraft Design")
        sc_layout = QFormLayout()
        
        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.1, 10000.0)
        self.mass_input.setValue(10.0)
        self.mass_input.setSuffix(" kg")
        
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(1.0, 100000.0)
        self.area_input.setValue(100.0)
        self.area_input.setSuffix(" m²")
        
        self.refl_input = QDoubleSpinBox()
        self.refl_input.setRange(0.0, 1.0)
        self.refl_input.setSingleStep(0.05)
        self.refl_input.setValue(0.9)
        
        sc_layout.addRow("Mass:", self.mass_input)
        sc_layout.addRow("Sail Area:", self.area_input)
        sc_layout.addRow("Reflectivity:", self.refl_input)
        sc_group.setLayout(sc_layout)
        layout.addWidget(sc_group)
        
        # 2. Orbit Parameters
        orbit_group = QGroupBox("Initial Orbit")
        orbit_layout = QFormLayout()
        
        self.orbit_type = QComboBox()
        self.orbit_type.addItems(["LEO (Earth)", "Heliocentric"])
        self.orbit_type.currentTextChanged.connect(self.update_orbit_fields)
        
        self.alt_input = QDoubleSpinBox() # Altitude or Distance
        self.alt_input.setRange(100.0, 1e9)
        self.alt_input.setValue(700.0)
        self.alt_label = QLabel("Altitude (km):")
        
        self.inc_input = QDoubleSpinBox()
        self.inc_input.setRange(0.0, 180.0)
        self.inc_input.setValue(28.5)
        self.inc_input.setSuffix(" deg")
        
        orbit_layout.addRow("Type:", self.orbit_type)
        orbit_layout.addRow(self.alt_label, self.alt_input)
        orbit_layout.addRow("Inclination:", self.inc_input)
        orbit_group.setLayout(orbit_layout)
        layout.addWidget(orbit_group)
        
        # 3. Environment/Physics 
        phys_group = QGroupBox("Physics Model")
        phys_layout = QVBoxLayout()
        
        self.check_j2 = QCheckBox("J2 Perturbation")
        self.check_j2.setChecked(True)
        self.check_drag = QCheckBox("Atmospheric Drag")
        self.check_drag.setChecked(True)
        self.check_srp = QCheckBox("Solar Radiation Pressure")
        self.check_srp.setChecked(True)
        self.check_eclipse = QCheckBox("Eclipse Model")
        self.check_eclipse.setChecked(True)
        
        phys_layout.addWidget(self.check_j2)
        phys_layout.addWidget(self.check_drag)
        phys_layout.addWidget(self.check_srp)
        phys_layout.addWidget(self.check_eclipse)
        phys_group.setLayout(phys_layout)
        layout.addWidget(phys_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def update_orbit_fields(self, text):
        if text == "LEO (Earth)":
            self.alt_label.setText("Altitude (km):")
            self.alt_input.setValue(700.0)
            self.inc_input.setEnabled(True)
        else:
            self.alt_label.setText("Distance (AU):")
            self.alt_input.setValue(1.0)
            self.inc_input.setEnabled(False) # Simplified for now

    def get_config(self):
        """Construct config dictionary from inputs."""
        # Orbit Logic
        current_type = self.orbit_type.currentText()
        if current_type == "LEO (Earth)":
            orbit_conf = {
                'type': 'LEO',
                'altitude_km': self.alt_input.value(),
                'inclination_deg': self.inc_input.value()
            }
        else:
            orbit_conf = {
                'type': 'Heliocentric',
                'distance_au': self.alt_input.value()
            }
            
        return {
            'spacecraft': {
                'mass': self.mass_input.value(),
                'sail_area': self.area_input.value(),
                'reflectivity': self.refl_input.value(),
                'inertia': [[1,0,0],[0,1,0],[0,0,1]] # Default
            },
            'orbit': orbit_conf,
            'physics': {
                'gravity_model': 'multi_body', # Default
                'perturbations': {
                    'j2': self.check_j2.isChecked(),
                    'drag': self.check_drag.isChecked(),
                    'srp': self.check_srp.isChecked(),
                    'eclipse': self.check_eclipse.isChecked()
                },
                'integrator': 'rk45', # Could add selector
                'navigation': True
            },
            'mission': {
                'step_size': 60.0, # Could expose
                'duration_days': 10.0 # Expose in Main Window or here
            }
        }
