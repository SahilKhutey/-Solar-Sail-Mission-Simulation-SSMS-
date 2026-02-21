import pytest
import numpy as np
from lincore.environment.ephemeris import get_body_state

def test_ephemeris_core_logic():
    """Trigger the ephemeris loader to ensure basic coverage of data loading pathways."""
    
    # The module caches the ephemeris object internally
    # We can fetch states which forces lazy loading
    state_earth = get_body_state("earth", t=0.0)
    assert state_earth is not None
    assert len(state_earth) == 6
    
    state_mars = get_body_state("mars", t=1000.0)
    assert state_mars is not None
    assert len(state_mars) == 6
    
    # Check invalid body
    with pytest.raises(Exception):
         get_body_state("pluto", t=0.0)
