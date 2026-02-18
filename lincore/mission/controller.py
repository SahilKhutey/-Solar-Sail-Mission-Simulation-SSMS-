from lincore.mission.pipeline import SolarSailMission
from lincore.utils.config_loader import validate_config

class MissionController:
    """
    Bridge between GUI and Simulation Engine.
    Handles configuration validation and mission execution.
    """
    def __init__(self):
        self.mission = None
        self.history = []

    def validate_config(self, config):
        # Basic validation wrapper
        try:
            # Add defaults if missing for GUI convenience
            if 'output' not in config:
                config['output'] = {'log_file': 'gui_mission.csv'}
            return True, "Config Valid"
        except Exception as e:
            return False, str(e)

    def run_mission(self, config, callback=None):
        """
        Run mission with optional progress callback.
        callback(progress_float, status_string)
        """
        self.mission = SolarSailMission(config)
        
        duration = config['mission']['duration_days'] * 86400.0
        step_size = config['mission']['step_size']
        total_steps = int(duration / step_size)
        
        self.history = [] # Reset history
        
        t = 0
        step_count = 0
        
        # Subsample for GUI memory management (max 10k points?)
        plot_interval = max(1, total_steps // 5000) 
        
        while t < duration:
            t, state = self.mission.step()
            step_count += 1
            
            # Store history for plotting
            if step_count % plot_interval == 0:
                # state: [rx, ry, rz, vx, vy, vz, q...]
                # We save dict for easy DataFrame conversion
                self.history.append({
                    't': t,
                    'rx': state[0], 'ry': state[1], 'rz': state[2],
                    'vx': state[3], 'vy': state[4], 'vz': state[5]
                })
            
            # Callback update (e.g., every 100 steps)
            if callback and step_count % 100 == 0:
                progress = min(t / duration, 1.0)
                callback(progress, f"Simulating Day {t/86400:.2f}...")
                
        if callback:
            callback(1.0, "Simulation Complete.")
            
        return self.history
