import numpy as np
from dataclasses import dataclass

@dataclass
class State:
    """
    Represents the full state of the spacecraft.
    Standard State Vector (13 elements):
    [0:3] Position (r) [km]
    [3:6] Velocity (v) [km/s]
    [6:10] Attitude Quaternion (q) [scalar, i, j, k]
    [10:13] Angular Velocity (w) [rad/s]
    """
    t: float
    r: np.ndarray
    v: np.ndarray
    q: np.ndarray
    w: np.ndarray
    mass: float = 10.0 # kg, can change with propellant use (if any)
    
    @property
    def vector(self):
        """Returns the flat numpy array for the integrator."""
        return np.concatenate((self.r, self.v, self.q, self.w))
    
    @classmethod
    def from_vector(cls, t, y, mass=10.0):
        """Reconstructs State from flat vector."""
        r = y[0:3]
        v = y[3:6]
        q = y[6:10]
        w = y[10:13]
        return cls(t, r, v, q, w, mass)
    
    def __repr__(self):
        return f"State(t={self.t:.2f}, r={self.r}, v={self.v})"
