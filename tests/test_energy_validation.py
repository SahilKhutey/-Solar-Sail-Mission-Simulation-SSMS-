import pytest
from lincore.validation.check_energy import check_energy_conservation
from lincore.validation.check_attitude import check_torque_free_motion

def test_energy_calculator():
    """Run the standalone validation scripts to ensure they don't crash."""
    # These functions run their own simulation loops and print results
    check_energy_conservation()
    
def test_attitude_calculator():
    check_torque_free_motion()
