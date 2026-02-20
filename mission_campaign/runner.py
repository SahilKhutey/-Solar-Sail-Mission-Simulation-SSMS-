import os
import sys
import numpy as np
import logging
from typing import Dict, Any

# Ensure we can import lincore
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lincore.mission.pipeline import SolarSailMission
from mission_recorder.recorder import Recorder
from mission_recorder.metadata_logger import MetadataLogger

class ResearchMission(SolarSailMission):
    """
    Extended mission class for research campaign.
    Adds steering laws and recording hooks.
    """
    def __init__(self, config: Dict[str, Any], steering_law: str = 'fixed'):
        super().__init__(config)
        self.steering_law = steering_law
        
    def _get_control_torque(self, state):
        if self.steering_law == 'fixed':
            return np.zeros(3)
        elif self.steering_law == 'optimal_direction':
            # Placeholder for optimal steering: Point normal to sun vector?
            # For now, just a simple rotation
            return np.array([0, 0, 1e-6]) 
        return np.zeros(3)

def map_params_to_config(params: Dict[str, Any], base_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps flat parameter dictionary to the nested config structure.
    """
    import copy
    config = copy.deepcopy(base_config)
    
    # Map Spacecraft
    if 'sail_area' in params:
        config['spacecraft']['sail_area'] = params['sail_area']
    if 'sail_mass' in params:
        config['spacecraft']['mass'] = params['sail_mass'] # Note: strictly mapped to mass
    if 'reflectivity' in params:
        config['spacecraft']['reflectivity'] = params['reflectivity']
        
    # Map Orbit
    if 'launch_altitude' in params:
        config['orbit']['altitude_km'] = params['launch_altitude']
        
    # Map Physics/Mission
    # steering_law is handled separately in runner
    
    # Ensure navigation key exists (SensorModel dependency)
    if 'navigation' not in config:
        config['navigation'] = {
            'position_noise_km': 0.010,
            'velocity_noise_kms': 0.001,
            'attitude_noise_deg': 0.01,
            'rate_noise_deg_s': 0.001
        }
        
    return config

def run_single_mission(run_id: str, params: Dict[str, Any], output_dir: str, base_config_path: str = 'config/mission_default.yaml', physics_eval_config: Dict[str, Any] = None):
    """
    Executes a single mission run.
    """
    from lincore.utils.config_loader import load_config
    
    # Load base config
    try:
        base_config = load_config(base_config_path)
    except Exception as e:
        print(f"Error loading base config: {e}")
        return {'status': 'failed', 'error': str(e)}

    # Map parameters
    config = map_params_to_config(params, base_config)
    
    # Apply Physics Overrides from Campaign Config
    if physics_eval_config:
        if 'physics' not in config: config['physics'] = {}
        config['physics'].update(physics_eval_config)
    
    # Setup recorder
    run_dir = os.path.join(output_dir, run_id)
    recorder = Recorder(run_dir)
    
    # Save effective config
    recorder.start_recording(config)
    
    # Initialize Mission
    steering_law = params.get('steering_law', 'fixed')
    try:
        mission = ResearchMission(config, steering_law=steering_law)
        
        duration_days = config['mission'].get('duration_days', 10.0)
        max_time = duration_days * 86400.0
        dt = config['mission'].get('step_size', 60.0)
        
        # Run Loop
        print(f"Run {run_id}: Starting simulation ({duration_days} days)...")
        last_print_time = 0.0
        while mission.time < max_time:
            t, state_list = mission.step()
            
            # Record
            # state_list is [rx, ry, rz, vx, vy, vz]
            # We can calculate derived metrics here
            r = np.array(state_list[:3])
            v = np.array(state_list[3:])
            
            metrics = {
                'energy': 0.5 * np.linalg.norm(v)**2 - 398600.4418 / np.linalg.norm(r),
                'solar_distance': np.linalg.norm(r) # Approximation if heliocentric
            }
            
            recorder.record_step(t, state_list, metrics)
            
            # Progress Log
            if t - last_print_time >= 86400.0: # Every day
                print(f"Run {run_id}: T={t/86400:.1f} days, dt={mission.dt:.4f}s")
                last_print_time = t
            elif t < 100.0 and (t - last_print_time >= 10.0): # Initial debug for slow starts
                 print(f"Run {run_id}: T={t:.1f}s, dt={mission.dt:.4f}s")
                 last_print_time = t
            
        print(f"Run {run_id}: Completed.")
        
        # Calculate summary metrics BEFORE finishing (which clears buffer)
        final_energy = metrics['energy'] 
        min_distance = min(recorder.buffer['solar_distance'])
        
        recorder.finish_recording()
        max_stress = 0.0 # Placeholder as stress not yet modeled
        escape_flag = final_energy > 0
        
        # Extract metadata
        meta = recorder.metadata_logger.metadata
        git_hash = meta.get('git', {}).get('commit_hash', 'unknown')
        start_time = meta.get('execution', {}).get('timestamp', '')
        
        # Calculate secondary metrics
        r_mag = np.linalg.norm(r)
        v_mag = np.linalg.norm(v)
        escape_vel = np.sqrt(2 * 398600.4418 / r_mag)
        
        return {
            'status': 'completed',
            'run_id': run_id,
            'final_time': mission.time,
            'time_of_flight': mission.time, # explicit key for DB
            'final_energy': final_energy,
            'min_distance_sun': min_distance,
            'escape_velocity': escape_vel,
            'max_stress': max_stress,
            'max_temp': 0.0, # Placeholder
            'escape_flag': escape_flag,
            'structural_failure': False, # Placeholder
            'thermal_failure': False, # Placeholder
            'stability_score': 1.0, # Placeholder
            'convergence_flag': True,
            'git_hash': git_hash,
            'start_time': start_time
        }
        
    except Exception as e:
        print(f"Run {run_id} failed: {e}")
        # Log failure
        import traceback
        traceback.print_exc()
        return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Run a single solar sail mission simulation.")
    parser.add_argument("config_file", help="Path to the configuration YAML file.")
    parser.add_argument("--output_dir", default="campaign_data", help="Directory to save results.")
    parser.add_argument("--run_id", default="manual_run", help="Identifier for this run.")
    
    args = parser.parse_args()
    
    print(f"Executing Mission from {args.config_file}...")
    result = run_single_mission(
        run_id=args.run_id,
        params={}, 
        output_dir=args.output_dir,
        base_config_path=args.config_file
    )
    
    # Save result to metadata manually if needed, but recorder handles it.
    # Just print result for debug
    print(json.dumps(result, indent=2, default=str))
