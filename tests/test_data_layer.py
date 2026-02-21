import sys
import os
import numpy as np
import yaml

# Add parent path
sys.path.append(os.path.abspath('.'))

from lincore.utils.config_loader import load_config, validate_config
from lincore.utils.logger import MissionLogger

def test_config():
    print("Testing Config Loader...")
    config_path = "config/mission_default.yaml"
    try:
        cfg = load_config(config_path)
        validate_config(cfg)
        print("Config Loaded Successfully:")
        print(f"  Mission: {cfg['mission']['name']}")
        print(f"  Mass: {cfg['spacecraft']['mass']}")
    except Exception as e:
        print(f"Config FAILED: {e}")

def test_logger():
    print("\nTesting Logger...")
    log_file = "test_log.csv"
    if os.path.exists(log_file):
        os.remove(log_file)
        
    logger = MissionLogger(log_file)
    
    # Fake state
    t = 0.0
    dt = 1.0
    state = np.zeros(14)
    extras = {"energy": -1.5, "h_mag": 2.0}
    
    logger.log_state(t, dt, state)
    logger.log_state(t+dt, dt, state)
    logger.close()
    
    # Verify content
    with open(log_file, 'r') as f:
        lines = f.readlines()
        print(f"Log Lines: {len(lines)}")
        print(f"Header: {lines[0].strip()}")
        print(f"Data 1: {lines[1].strip()}")
        
    if len(lines) == 3:
        print("Logger PASS")
    else:
        print("Logger FAIL")
        
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)

if __name__ == "__main__":
    test_config()
    test_logger()
