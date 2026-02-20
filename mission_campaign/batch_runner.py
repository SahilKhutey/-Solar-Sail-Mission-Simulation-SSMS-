import os
import sys
import yaml
import json
import time
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any

# Ensure we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mission_campaign.parameter_space import ParameterSpace
from mission_campaign.sampler import Sampler
from mission_campaign.runner import run_single_mission
from research_database.db_manager import DatabaseManager

def load_campaign_config(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def run_wrapper(args):
    """Wrapper for multiprocessing which takes a single tuple argument."""
    run_id, params, output_dir, base_config_path, physics_config = args
    try:
        start_t = time.time()
        result = run_single_mission(run_id, params, output_dir, base_config_path, physics_eval_config=physics_config)
        duration = time.time() - start_t
        
        # Add metadata for DB
        result['run_id'] = run_id
# ... (rest of wrapper)

    # ... inside BatchRunner.run ...

        # 2. Execution Setup
        num_workers = self.config['execution'].get('num_workers', 1)
        base_config_path = 'config/mission_default.yaml' # Could be configurable
        physics_config = self.config.get('physics', {}) # Campaign overrides
        
        tasks = []
        for i, params in enumerate(samples):
            run_id = f"run_{i:06d}"
            tasks.append((run_id, params, self.output_dir, base_config_path, physics_config))
        result['duration_seconds'] = duration
        result.update(params) # Flatten params for DB if needed
        return result
    except Exception as e:
        return {'status': 'failed', 'run_id': run_id, 'error': str(e)}

class BatchRunner:
    def __init__(self, config_path: str):
        self.config = load_campaign_config(config_path)
        self.output_dir = self.config['output'].get('base_dir', 'campaign_data')
        self.db = DatabaseManager()
        
    def run(self):
        print(f"Starting Campaign: {self.config.get('campaign_name')}")
        
        # 1. Parameter Generation
        param_space = ParameterSpace(self.config)
        sampler = Sampler(param_space, seed=self.config['sampling'].get('seed', 42))
        
        num_samples = self.config['sampling'].get('num_samples', 10)
        print(f"Generating {num_samples} samples using {self.config['sampling']['method']}...")
        
        if self.config['sampling']['method'] == 'latin_hypercube':
            samples = sampler.generate_lhs_samples(num_samples)
        elif self.config['sampling']['method'] == 'sobol':
            samples = sampler.generate_sobol_samples(num_samples)
        else:
            # Fallback or other methods
             samples = sampler.generate_lhs_samples(num_samples)
             
        # 2. Execution Setup
        num_workers = self.config['execution'].get('num_workers', 1)
        base_config_path = 'config/mission_default.yaml' # Could be configurable
        
        tasks = []
        physics_config = self.config.get('physics', {})
        for i, params in enumerate(samples):
            run_id = f"run_{i:06d}"
            tasks.append((run_id, params, self.output_dir, base_config_path, physics_config))
            
        print(f"Launching {len(tasks)} runs on {num_workers} workers...")
        
        results = []
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(run_wrapper, t): t for t in tasks}
            
            for future in as_completed(futures):
                res = future.result()
                results.append(res)
                print(f"Finished {res.get('run_id')}: {res.get('status')}")
                
                # 3. Database Logging
                self.log_result(res)
                
        print("Campaign Batch Completed.")
        
    def log_result(self, result: Dict[str, Any]):
        if result.get('status') == 'completed':
            # Add campaign_id
            result['campaign_id'] = self.config.get('campaign_name', 'default')
            
            # Ensure all keys in result match schema or are ignored by insert_run if robust
            # Our db_manager expects keys like: sail_area, mass, etc.
            # result has params (flattened in run_wrapper) and outcomes.
            
            self.db.insert_run(result)
        else:
            print(f"Skipping DB log for failed run: {result.get('run_id')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help="Path to campaign config")
    args = parser.parse_args()
    
    runner = BatchRunner(args.config)
    runner.run()
