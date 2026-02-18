import sys
import os
import argparse

# Add parent path
sys.path.append(os.path.abspath('.'))

from lincore.utils.config_loader import load_config
from lincore.mission.pipeline import SolarSailMission

def main():
    parser = argparse.ArgumentParser(description="Run Solar Sail Mission Simulation")
    parser.add_argument('config', nargs='?', default='config/mission_default.yaml', help="Path to mission config file")
    args = parser.parse_args()
    
    print(f"Loading config from {args.config}...")
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    print("Initializing Mission...")
    mission = SolarSailMission(config)
    
    duration = config['mission'].get('duration_days', 1.0)
    print(f"Starting Simulation for {duration} days...")
    
    mission.run(duration)
    
    print("Done.")

if __name__ == "__main__":
    main()
