"""
Shared configuration schemas and data structures for the Solar Sail Campaign.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json

@dataclass
class SimulationConfig:
    """Configuration for a single simulation run."""
    run_id: str
    parameters: Dict[str, Any]
    physics_settings: Dict[str, Any]
    output_settings: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    @classmethod
    def from_json(cls, json_str: str) -> 'SimulationConfig':
        data = json.loads(json_str)
        return cls(**data)

@dataclass
class CampaignState:
    """State tracking for the entire campaign."""
    campaign_id: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    active_runs: int
    status: str # 'initializing', 'running', 'completed', 'paused'

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
