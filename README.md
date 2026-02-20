# Solar Sail Mission Simulation (SSMS)

![Status](https://img.shields.io/badge/status-stable-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

**A NASA-Grade, High-Fidelity Solar Sail Analysis Platform.**

SSMS is a comprehensive research tool designed for the design, optimization, and analysis of solar sail missions. It integrates rigorous physics models with modern software engineering practices to provide a robust environment for astrodynamics research.

---

## 🌟 Key Features

### 🔬 High-Fidelity Physics Engine
-   **N-Body Gravity**: JIT-compiled perturbation model including Earth, Moon, Jupiter, Mars, and Venus with true ephemeris origins.
-   **Numerical Stability**: Adaptive Runge-Kutta-Fehlberg (RKF45) integration featuring IEEE Mixed Tolerances (`atol + rtol * |y|`) for extreme proximity safety.
-   **Advanced SRP**: Solar Radiation Pressure model with conical shadow handling and variable solar flux.
-   **Perturbations**: $J_2$ zonal harmonics and exponential atmospheric drag for LEO operations.

### 🚀 Mission Design & Optimization
-   **Trajectory Optimization**: Direct Transcription (Collocation) solver and Differential Evolution (`scipy.optimize`) for optimal interplanetary transfers.
-   **Research Campaign System**: Automated batch execution, data recording (`parquet`), and reporting for large-scale parametric studies (`mission_campaign`).
-   **Machine Learning Surrogate**: Gradient Boosting predictors to instantly estimate Final Energy and Escape Velocity from design parameters.

### 🎮 Interactive Mission Control
-   **PyQt6 Desktop**: Professional GUI for real-time local mission monitoring.
-   **Streamlit Web Dashboard** (`dashboard/app.py`): Cloud-ready interactive research portal.
-   **Visualization**: Real-time Ephemeris mapping (Plotly 3D), Target distance tracking, and interactive dataset scatter plots with 5,000+ point memory safety.

### ⚡ Performance
-   **Numba FastMath JIT**: Core dynamics loops optimized with aggressive algebraic unrolling for near-C performance (`lincore/utils/jit.py`).
-   **Vectorized**: Fully vectorized force models for rapid propagation and parallel database batching.

---

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/SahilKhutey/-Solar-Sail-Mission-Simulation-SSMS-.git
    cd -Solar-Sail-Mission-Simulation-SSMS-
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional) Download SPICE Kernels**:
    ```bash
    python lincore/environment/download_kernels.py
    ```

---

## 🚀 Usage

### 🌐 Web Dashboard (Recommended)
The fastest way to analyze campaign data, run custom targets, and view ML predictions.
```bash
python -m streamlit run dashboard/app.py
```
*Access features like the **Design Space Explorer**, **3D Trajectory Viewer (with real target ephemeris)**, and the **Custom Mission Designer**.*

### Graphical User Interface (GUI)
Launch the mission control dashboard:
```bash
python lincore/gui/app.py
```
*Configure orbit parameters, force models, and visualization settings directly from the UI.*

### Headless Simulation
Run a simulation from a configuration file:
```bash
python run_mission.py config/mission_default.yaml
```

### Research Scripts
-   **Optimization**: `python tests/test_optimization.py`
-   **Sensitivity Analysis**: `python tests/test_sensitivity.py`
-   **Monte Carlo**: `python lincore/analysis/monte_carlo.py`

### Research Campaign (Automated)
The recommended way to run a large-scale campaign is using the automation script, which handles database locking, progress monitoring, and auto-reporting.

```bash
python run_and_report.py
```

### Manual Campaign Execution
Alternatively, you can run components individually:

1. **Run Batch**:
   ```bash
   python mission_campaign/batch_runner.py mission_campaign/campaign_config.yaml
   ```
2. **Generate Report** (Requires DB Snapshot if running):
   ```bash
   python reporting_engine/report_builder.py SolarSail_Research_Campaign_v1 --db_path temp.db
   ```

### Troubleshooting
If the database and files get out of sync (e.g. after a crash):
```bash
python recover_db.py
```
This will scan `campaign_data/` and re-populate `mission_data.db`.

---

## 📂 Project Structure

```
Solar-Sail/
├── lincore/               # Main Package
│   ├── core/              # State, Dynamics, Integrators
│   ├── forces/            # Gravity, SRP, Drag, N-Body
│   ├── optimization/      # Trajectory Optimizers
│   ├── analysis/          # Monte Carlo, Sensitivity, Metrics
│   ├── gui/               # PyQt6 Application
│   └── environment/       # Ephemeris & Atmosphere
├── mission_campaign/      # Research Campaign Manager
├── mission_recorder/      # High-Fidelity Data Logging
├── research_database/     # SQLite Metrics Storage
├── reporting_engine/      # Automated PDF Report Generator
├── config/                # Mission Configuration (YAML)
├── docs/                  # Sphinx Documentation
├── tests/                 # Verification Suite
└── legacy/                # Archived Prototypes
```

---

## 📚 Citation

If you use this software in your research, please cite it using the metadata in `CITATION.cff` or:

> Mission Team. (2026). Solar Sail Mission Simulation (SSMS) [Computer software]. https://github.com/SahilKhutey/-Solar-Sail-Mission-Simulation-SSMS-

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.