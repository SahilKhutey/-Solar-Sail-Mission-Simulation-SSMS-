import csv
import os
import time
import numpy as np

try:
    import h5py
    HAS_H5 = True
except ImportError:
    HAS_H5 = False

class MissionLogger:
    def __init__(self, filepath, format='csv', buffer_size=1000):
        self.filepath = filepath
        self.format = format
        self.buffer = []
        self.buffer_size = buffer_size
        self.start_time = time.time()
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        if self.format == 'csv':
            self._init_csv()
        elif self.format == 'hdf5':
            if not HAS_H5:
                print("H5PY not found. Falling back to CSV.")
                self.format = 'csv'
                self.filepath = self.filepath.replace('.h5', '.csv')
                self._init_csv()
            else:
                self._init_hdf5()
                
    def _init_csv(self):
        # Write Header
        with open(self.filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Standard extended state header
            header = ['t', 'dt', 'rx', 'ry', 'rz', 'vx', 'vy', 'vz', 
                      'q0', 'q1', 'q2', 'q3', 'wx', 'wy', 'wz', 'mass']
            writer.writerow(header)

    def _init_hdf5(self):
        # Create file and datasets
        # We will append, so enable chunking
        with h5py.File(self.filepath, 'w') as f:
            # Create resizable datasets
            # Time column
            f.create_dataset('time', (0,), maxshape=(None,), dtype='f8', chunks=(1000,))
            # State vector (rx, ry, rz, vx, vy, vz, q..., w..., m) = 14 elements
            f.create_dataset('state', (0, 14), maxshape=(None, 14), dtype='f8', chunks=(1000, 14))
            
            # Metadata
            f.attrs['created_at'] = str(time.time())

    def log_state(self, t, dt, state):
        """
        Log state vector.
        state: np.array of size 14 or State object
        """
        # Convert State object to array if needed
        if hasattr(state, 'vector'):
             vec = state.vector
             # Append mass if not in vector (vector is 13, mass is 14th)
             # State.vector returns 13 elements. 
             # Let's concatenate mass.
             row = np.concatenate(([t, dt], vec, [state.mass]))
        else:
             # Assume state is already full vector (legacy pipeline usage)
             # But legacy pipeline passed state (14 elem) separately from t
             # Let's handle list/array
             row = list(state)
             row.insert(0, dt)
             row.insert(0, t)
             
        self.buffer.append(row)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush()
            
    def flush(self):
        if not self.buffer: return
        
        if self.format == 'csv':
            with open(self.filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.buffer)
        
        elif self.format == 'hdf5':
            with h5py.File(self.filepath, 'a') as f:
                dset_t = f['time']
                dset_s = f['state']
                
                # Current size
                current_len = dset_t.len()
                add_len = len(self.buffer)
                
                # Resize
                dset_t.resize((current_len + add_len,))
                dset_s.resize((current_len + add_len, 14))
                
                # Prepare data
                data = np.array(self.buffer)
                # data layout: [t, dt, r, v, q, w, m]
                # t is col 0. state is col 2..15? 
                # wait, log_state constructed: [t, dt, r..., v..., q..., w..., m]
                # Total 2 (t, dt) + 3+3+4+3 (13) + 1 (m) = 16 columns?
                
                # HDF5 structure: 'time' = t. 'state' = rest?
                # Let's stick to simplest:
                # time dataset -> col 0
                # state dataset -> col 2 onwards (skip dt for now or add it?)
                # Actually, let's just dump simple.
                
                times = data[:, 0]
                states = data[:, 2:] # Skip t, dt
                
                dset_t[current_len:] = times
                dset_s[current_len:] = states
                
        self.buffer = []
        
    def close(self):
        self.flush()
