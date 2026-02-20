import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

DB_PATH = "research_database/mission_data.db"
OUTPUT_DIR = "reports/EDA_Analysis"

def load_data():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    query = """
    SELECT 
        run_id, sail_area, mass, reflectivity, thickness, launch_altitude,
        final_energy, time_of_flight, min_distance_sun, escape_flag, duration_seconds
    FROM campaign_runs
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_distributions(df):
    print("Generating distribution plots...")
    metrics = ['final_energy', 'time_of_flight', 'min_distance_sun']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for i, col in enumerate(metrics):
        sns.histplot(data=df, x=col, hue='escape_flag', element="step", ax=axes[i])
        axes[i].set_title(f"Distribution of {col}")
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/distributions.png")
    plt.close()

def plot_correlations(df):
    print("Generating correlation matrix...")
    # Select numeric columns only
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Feature Correlation Matrix")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/correlation_matrix.png")
    plt.close()

def plot_pairplot(df):
    print("Generating pair plot (this may take a moment)...")
    # Downsample if too large to save time
    if len(df) > 1000:
        plot_df = df.sample(1000)
    else:
        plot_df = df
        
    cols = ['sail_area', 'mass', 'final_energy', 'min_distance_sun', 'escape_flag']
    sns.pairplot(plot_df[cols], hue='escape_flag', diag_kind='hist')
    plt.savefig(f"{OUTPUT_DIR}/pairplot.png")
    plt.close()

def plot_escape_map(df):
    print("Generating escape heatmaps...")
    plt.figure(figsize=(10, 8))
    
    # Scatter plot with size/color
    sc = plt.scatter(
        df['sail_area'], 
        df['mass'], 
        c=df['final_energy'], 
        cmap='viridis', 
        s=50, 
        alpha=0.6,
        edgecolors='w', linewidth=0.5
    )
    plt.colorbar(sc, label='Final Energy (J/kg)')
    plt.xlabel('Sail Area (m^2)')
    plt.ylabel('Mass (kg)')
    plt.title('Design Space Analysis: Area vs Mass vs Energy')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/design_space_energy.png")
    plt.close()

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading data from database...")
    df = load_data()
    print(f"Loaded {len(df)} runs.")
    
    if len(df) < 10:
        print("Not enough data for meaningful analysis.")
        return

    plot_distributions(df)
    plot_correlations(df)
    plot_pairplot(df)
    plot_escape_map(df)
    
    print(f"\nAnalysis Complete. Plots saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
