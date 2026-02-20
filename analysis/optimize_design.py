import pickle
import numpy as np
import os
import pandas as pd
from scipy.optimize import differential_evolution, minimize

MODEL_DIR = "analysis/models"
REPORT_DIR = "reports/Optimization"

# Define bounds based on campaign_config.yaml (approximate)
# Area: 1000 - 25000 m^2
# Mass: 10 - 500 kg
# Reflectivity: 0.8 - 1.0
# Thickness: 2.0 - 10.0 microns
# Altitude: 5000 - 50000 km
# Bounds from campaign_config.yaml
BOUNDS = [
    (1000.0, 100000.0), # sail_area
    (10.0, 500.0),      # mass
    (0.7, 0.99),        # reflectivity
    (1.0, 10.0),        # thickness
    (400.0, 35786.0)    # launch_altitude
]
PARAM_NAMES = ['sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude']

def load_models():
    with open(os.path.join(MODEL_DIR, "surrogate_energy.pkl"), "rb") as f:
        model_energy = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "surrogate_distance.pkl"), "rb") as f:
        model_dist = pickle.load(f)
    return model_energy, model_dist

def objective(x, model_energy, model_dist):
    # x is [area, mass, refl, thick, alt]
    X_in = pd.DataFrame([x], columns=PARAM_NAMES)
    
    energy_pred = model_energy.predict(X_in)[0]
    dist_pred = model_dist.predict(X_in)[0]
    
    # We want to MAXIMIZE Energy.
    # If Energy < 0, it's bound. We want Energy > 0.
    # Convert to minimization problem: minimize -Energy
    
    # CONSTRAINT: Min Distance from Sun > 0.2 AU (30 million km) to be thermally safe-ish
    # (Sun radius ~0.7 million km, Mercury ~58 million km)
    SAFE_DIST_KM = 30000000.0 
    
    penalty = 0.0
    if dist_pred < SAFE_DIST_KM:
        # Penalize violation heavily
        penalty += 1e6 * (SAFE_DIST_KM - dist_pred) / SAFE_DIST_KM
        
    return -energy_pred + penalty

def optimize(model_energy, model_dist):
    print("Starting Global Optimization (Differential Evolution)...")
    
    result = differential_evolution(
        objective,
        bounds=BOUNDS,
        args=(model_energy, model_dist),
        strategy='best1bin',
        maxiter=1000,
        popsize=15,
        tol=0.01,
        mutation=(0.5, 1),
        recombination=0.7,
        disp=True
    )
    
    return result

def main():
    if not os.path.exists(MODEL_DIR):
        print("Models not found. Train them first.")
        return
        
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    model_energy, model_dist = load_models()
    
    res = optimize(model_energy, model_dist)
    
    print("\n--- OPTIMIZATION RESULTS ---")
    print(f"Success: {res.success}")
    print(f"Message: {res.message}")
    print(f"Iterations: {res.nit}")
    
    best_params = res.x
    print("\nOptimal Configuration:")
    for name, val in zip(PARAM_NAMES, best_params):
        print(f"  {name}: {val:.4f}")
        
    # Verify Prediction
    X_in = pd.DataFrame([best_params], columns=PARAM_NAMES)
    energy = model_energy.predict(X_in)[0]
    dist = model_dist.predict(X_in)[0]
    
    print(f"\nPredicted Outcome:")
    print(f"  Final Energy: {energy:.2f} J/kg")
    print(f"  Min Distance: {dist:.2f} km")
    
    # Compute Beta (Accel/Gravity ratio) approximation for context
    # Beta ~ 1.53e-3 * Area / Mass (very roughly if reflectivity=1)
    # Actually accel = 2 * P * A * n / m
    # Just save results for now.
    
    with open(os.path.join(REPORT_DIR, "optimal_design.txt"), "w") as f:
        f.write(str(res))
        f.write(f"\n\nPredicted Energy: {energy}")

if __name__ == "__main__":
    main()
