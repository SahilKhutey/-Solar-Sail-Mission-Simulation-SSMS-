
import pickle
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

MODEL_DIR = "analysis/models"
REPORT_DIR = "reports/Sensitivity"

PARAM_NAMES = ['sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude']

def load_model():
    path = os.path.join(MODEL_DIR, "surrogate_energy.pkl")
    if not os.path.exists(path):
        print(f"Model not found at {path}")
        return None
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model

def analyze_sensitivity(model):
    # Using built-in feature importance from GradientBoostingRegressor
    # This is "impurity-based" importance. 
    # For more robust results, use permutation importance.
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("\nFeature Ranking:")
    results = []
    for f in range(len(PARAM_NAMES)):
        idx = indices[f]
        name = PARAM_NAMES[idx]
        score = importances[idx]
        print(f"{f+1}. {name}: {score:.4f}")
        results.append((name, score))

    # Plot
    plt.figure(figsize=(10, 6))
    plt.title("Solar Sail Design Sensitivity: Parameter Impact on Energy")
    plt.bar([x[0] for x in results], [x[1] for x in results], color='skyblue')
    plt.ylabel("Relative Importance")
    plt.xlabel("Design Parameter")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    plot_path = os.path.join(REPORT_DIR, "feature_importance.png")
    plt.savefig(plot_path)
    print(f"\nPlot saved to {plot_path}")
    
    return results

def main():
    model = load_model()
    if model:
        analyze_sensitivity(model)
        
if __name__ == "__main__":
    main()
