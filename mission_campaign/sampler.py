import numpy as np
from scipy.stats import qmc
from typing import List, Dict, Any
from .parameter_space import ParameterSpace

class Sampler:
    """
    Generates experimental designs using various sampling strategies.
    Default: Latin Hypercube Sampling (LHS).
    """
    def __init__(self, space: ParameterSpace, seed: int = 42):
        self.space = space
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_lhs_samples(self, n_samples: int) -> List[Dict[str, Any]]:
        """
        Generates N samples using Latin Hypercube Sampling.
        Returns a list of configuration dictionaries.
        """
        bounds = self.space.get_bounds()
        if not bounds:
            return [{}] * n_samples # No numerical parameters

        dim = len(bounds)
        sampler = qmc.LatinHypercube(d=dim, seed=self.seed)
        sample_unit = sampler.random(n=n_samples)
        
        # Scale samples to bounds
        l_bounds = [b[0] for b in bounds]
        u_bounds = [b[1] for b in bounds]
        
        scaled_samples = qmc.scale(sample_unit, l_bounds, u_bounds)
        
        configs = []
        for i in range(n_samples):
            # Create base config from numerical params
            config = self.space.map_sample_to_config(scaled_samples[i])
            
            # Handle categorical parameters (uniformly sample for now)
            # This is a simplification; true mixed-integer LHS is harder
            for name, p in self.space.parameters.items():
                if p.distribution == 'categorical':
                    config[name] = self.rng.choice(p.options)
            
            configs.append(config)
            
        return configs
    
    def generate_sobol_samples(self, n_samples: int) -> List[Dict[str, Any]]:
        """Generates Sobol sequence samples (must be power of 2 for best results)."""
        bounds = self.space.get_bounds()
        dim = len(bounds)
        # Sobol requires m where 2^m = n_samples roughly
        m = int(np.ceil(np.log2(n_samples)))
        sampler = qmc.Sobol(d=dim, scramble=True, seed=self.seed)
        sample_unit = sampler.random_base2(m=m)
        
        # Crop if we generated more than needed (though power of 2 is preferred)
        sample_unit = sample_unit[:n_samples]

        l_bounds = [b[0] for b in bounds]
        u_bounds = [b[1] for b in bounds]
        
        scaled = qmc.scale(sample_unit, l_bounds, u_bounds)
        
        configs = []
        for i in range(n_samples):
            config = self.space.map_sample_to_config(scaled[i])
             # Handle categorical
            for name, p in self.space.parameters.items():
                if p.distribution == 'categorical':
                    config[name] = self.rng.choice(p.options)
            configs.append(config)
            
        return configs
