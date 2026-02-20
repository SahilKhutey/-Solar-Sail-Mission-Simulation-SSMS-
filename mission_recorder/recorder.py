import os
import time
import shutil
from typing import Dict, Any, List
import numpy as np
from .metadata_logger import MetadataLogger
from .data_serializer import DataSerializer

class Recorder:
    """
    Main interface for recording simulation data.
    """
    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self.metadata_logger = MetadataLogger()
        self.serializer = DataSerializer()
        self.buffer: Dict[str, List[float]] = {
            'time': [],
            'x': [], 'y': [], 'z': [],
            'vx': [], 'vy': [], 'vz': [],
            'energy': []
            # Add other fields as needed
        }
        self.start_time = None

    def start_recording(self, config: Dict[str, Any]):
        """
        Initializes recording for a run.
        """
        os.makedirs(self.run_dir, exist_ok=True)
        self.start_time = time.time()
        self.metadata_logger.capture(config)
        
        # Save initial metadata
        self.metadata_logger.save(os.path.join(self.run_dir, 'run_metadata.json'))

    def record_step(self, t, state, metrics):
        """
        Records a single simulation step.
        state: [x, y, z, vx, vy, vz]
        metrics: dict of derived values
        """
        self.buffer['time'].append(t)
        self.buffer['x'].append(state[0])
        self.buffer['y'].append(state[1])
        self.buffer['z'].append(state[2])
        self.buffer['vx'].append(state[3])
        self.buffer['vy'].append(state[4])
        self.buffer['vz'].append(state[5])
        
        for k, v in metrics.items():
            if k not in self.buffer:
                self.buffer[k] = []
            self.buffer[k].append(v)

    def finish_recording(self):
        """
        Finalizes recording, saves data to disk.
        """
        # Save time-series
        ts_path = os.path.join(self.run_dir, 'trajectory.parquet')
        self.serializer.save_timeseries(self.buffer, ts_path)

        # Update metadata with duration and status
        duration = time.time() - self.start_time
        self.metadata_logger.metadata['execution']['duration_seconds'] = duration
        self.metadata_logger.metadata['execution']['status'] = 'completed'
        
        # Save final metadata (overwrite)
        self.metadata_logger.save(os.path.join(self.run_dir, 'run_metadata.json'))

        # Clear buffer
        self._clear_buffer()

    def _clear_buffer(self):
        for k in self.buffer:
            self.buffer[k] = []
