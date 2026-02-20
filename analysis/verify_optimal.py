
import sys
import os
import yaml
import json
import numpy as np
import pandas as pd

# Optimal parameters found by optimization (Hardcoded from previous output for simplicity, or read from file)
# Recopying from output:
# Area: 85306.0, Mass: 398.2, Refl: 0.826, Thick: 1.32, Alt: 35650.0
OPTIMAL_PARAMS = {
    'spacecraft': {
        'sail_area': 85306.0,
        'mass': 398.2,
        'reflectivity': 0.826,
        'thickness': 1.32
    },
    'orbit': {
        'altitude_km': 35650.0
    }
}

OUTPUT_DIR = "reports/Optimization/Verification_Run"

def main():
    print("Loading base configuration...")
    with open("mission_campaign/campaign_config.yaml", "r") as f:
        # This is a campaign config, we need a single run config structure
        # Let's load the template
        pass
        
    # Create a specific config for this run
    run_config = {
        'mission': {'name': 'Optimal Design Verification', 'duration_days': 100.0, 'step_size': 60.0}, # Extended duration to test escape!
        'spacecraft': OPTIMAL_PARAMS['spacecraft'],
        'orbit': {
            'type': 'LEO', 
            'altitude_km': OPTIMAL_PARAMS['orbit']['altitude_km'],
            'inclination_deg': 28.5,
            'eccentricity': 0.001
        },
        'physics': {
            'integrator': 'rk45',
            'perturbations': {'J2': True, 'drag': False, 'third_body': True}
        },
        'output': {
            'log_file': 'mission_log.csv',
            'log_interval': 60.0
        },
        'navigation': {'position_noise_km': 0.0, 'velocity_noise_kms': 0.0, 'attitude_noise_deg': 0.0, 'rate_noise_deg_s': 0.0}
    }
    
    # Add defaults missing
    run_config['spacecraft']['cd'] = 2.2
    run_config['spacecraft']['inertia'] = [[100,0,0],[0,100,0],[0,0,100]]
    run_config['spacecraft']['r_cp'] = [0.1, 0.1, 0.0]
    run_config['physics']['gravity_model'] = 'two_body' # or 'point_mass'
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Running Verification Simulation (Extended Duration: 100 days)...")
    # We need to adapt the runner to accept a dict, or save to yaml first
    config_path = os.path.join(OUTPUT_DIR, "optimal_config.yaml")
    with open(config_path, "w") as f:
        yaml.dump(run_config, f)
        
    # Run
    # runner.py usually takes a file path
    # We can import the simulation logic directly or use subprocess
    # Let's use the runner's main function if possible, or just call the physics engine
    # inspecting runner.py... better to run via command line to ensure environment consistency
    
    cmd = f"python mission_campaign/runner.py {config_path} --output_dir {OUTPUT_DIR}"
    os.system(cmd)
    
    print("\nVerification Complete.")
    print(f"Results saved to {OUTPUT_DIR}")
    
    # Check result
    meta_path = os.path.join(OUTPUT_DIR, "run_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
        status = meta.get('execution', {}).get('status')
        print(f"Status: {status}")
        
        # Calculate Energy if not present (runner might calculate it?)
        # Let's trust the runner output

if __name__ == "__main__":
    main()
