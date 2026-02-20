from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np

@dataclass
class ParameterDefinition:
    name: str
    min_val: float
    max_val: float
    distribution: str = "uniform" # uniform, log-uniform
    options: Optional[List[Any]] = None

class ParameterSpace:
    """
    Defines the multidimensional parameter space for the campaign.
    """
    def __init__(self, config: Dict[str, Any]):
        self.parameters = {}
        self._parse_config(config)

    def _parse_config(self, config: Dict[str, Any]):
        """Parses the YAML configuration to build parameter definitions."""
        params = config.get('parameters', {})
        for name, settings in params.items():
            dist = settings.get('distribution', 'uniform')
            if dist == 'categorical':
                self.parameters[name] = ParameterDefinition(
                    name=name,
                    min_val=0, max_val=0, # Not used for categorical
                    distribution=dist,
                    options=settings.get('options', [])
                )
            else:
                self.parameters[name] = ParameterDefinition(
                    name=name,
                    min_val=settings.get('min'),
                    max_val=settings.get('max'),
                    distribution=dist
                )

    def get_bounds(self) -> List[List[float]]:
        """Returns bounds for numerical parameters only."""
        bounds = []
        for name, p in self.parameters.items():
            if p.distribution != 'categorical':
                if p.distribution == 'log-uniform':
                    bounds.append([np.log10(p.min_val), np.log10(p.max_val)])
                else:
                    bounds.append([p.min_val, p.max_val])
        return bounds
    
    def get_numerical_param_names(self) -> List[str]:
        return [n for n, p in self.parameters.items() if p.distribution != 'categorical']

    def map_sample_to_config(self, sample_vector: np.ndarray) -> Dict[str, Any]:
        """Maps a normalized (or bounded) sample vector back to a configuration dictionary."""
        config = {}
        idx = 0
        for name, p in self.parameters.items():
            if p.distribution != 'categorical':
                val = sample_vector[idx]
                if p.distribution == 'log-uniform':
                    config[name] = float(10**val)
                else:
                    config[name] = float(val)
                idx += 1
            # Categorical handling would need a separate strategy or distinct index
        return config
