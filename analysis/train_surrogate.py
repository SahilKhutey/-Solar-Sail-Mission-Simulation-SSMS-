import sqlite3
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error

DB_PATH = "research_database/mission_data.db"
MODEL_DIR = "analysis/models"
REPORT_DIR = "reports/Surrogate_Analysis"

def load_data():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    query = """
    SELECT 
        sail_area, mass, reflectivity, thickness, launch_altitude,
        final_energy, min_distance_sun, escape_flag
    FROM campaign_runs
    WHERE final_energy IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def train_models(df):
    # Drop rows with any NaN values in standard columns
    df = df.dropna()
    print(f"Data after dropping NaNs: {len(df)} samples")

    # Features
    X = df[['sail_area', 'mass', 'reflectivity', 'thickness', 'launch_altitude']]
    
    # Targets
    y_energy = df['final_energy']
    y_dist = df['min_distance_sun']
    
    # Split
    X_train, X_test, y_en_train, y_en_test, y_dist_train, y_dist_test = train_test_split(
        X, y_energy, y_dist, test_size=0.2, random_state=42
    )
    
    print(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples.")
    
    # Model 1: Energy Predictor
    print("Training Energy Predictor...")
    model_energy = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    model_energy.fit(X_train, y_en_train)
    
    score_en = model_energy.score(X_test, y_en_test)
    print(f"Energy Model R^2: {score_en:.4f}")
    
    # Model 2: Perihelion Predictor (Safety)
    print("Training Min-Distance Predictor...")
    model_dist = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model_dist.fit(X_train, y_dist_train)
    
    score_dist = model_dist.score(X_test, y_dist_test)
    print(f"Distance Model R^2: {score_dist:.4f}")
    
    return {
        'energy': model_energy,
        'distance': model_dist,
        'scores': (score_en, score_dist),
        'X_cols': X.columns.tolist()
    }

def plot_feature_importance(model, feature_names, title, filename):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=importance[indices], y=np.array(feature_names)[indices], palette="viridis")
    plt.title(f"Feature Importance: {title}")
    plt.xlabel("Relative Importance")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, filename))
    plt.close()

def plot_prediction_scatter(y_true, y_pred, title, filename):
    plt.figure(figsize=(8, 8))
    plt.scatter(y_true, y_pred, alpha=0.5)
    
    # Ideal line
    min_val, max_val = min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    
    plt.xlabel("True Value (Physics Engine)")
    plt.ylabel("Predicted Value (ML Surrogate)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, filename))
    plt.close()

def main():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
        
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    df = load_data()
    print(f"Loaded {len(df)} runs.")
    
    results = train_models(df)
    
    # Save models
    with open(os.path.join(MODEL_DIR, "surrogate_energy.pkl"), "wb") as f:
        pickle.dump(results['energy'], f)
        
    with open(os.path.join(MODEL_DIR, "surrogate_distance.pkl"), "wb") as f:
        pickle.dump(results['distance'], f)
        
    print(f"Models saved to {MODEL_DIR}")
    
    # Analysis Plots
    plot_feature_importance(
        results['energy'], results['X_cols'], 
        "Impact on Final Energy", "importances_energy.png"
    )
    plot_feature_importance(
        results['distance'], results['X_cols'], 
        "Impact on Perihelion (Safety)", "importances_distance.png"
    )
    
    # Verification Plot (on full dataset for visualization)
    X = df[results['X_cols']]
    y_pred = results['energy'].predict(X)
    plot_prediction_scatter(
        df['final_energy'], y_pred, 
        f"Surrogate Accuracy (R^2 = {results['scores'][0]:.3f})", "prediction_parity.png"
    )

if __name__ == "__main__":
    main()
