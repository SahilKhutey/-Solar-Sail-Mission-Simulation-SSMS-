import math
import sys
import os

# Ensure we can import lincore
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lincore.dynamics import two_body, MU_EARTH
from lincore.integrators import rk4
from lincore.solar_sail_sim import specific_energy

def orbital_energy(state):
    x, y, z, vx, vy, vz = state
    r = math.sqrt(x*x + y*y + z*z)
    v2 = vx*vx + vy*vy + vz*vz

    return 0.5*v2 - MU_EARTH / r

def test_energy_conservation_two_body():
    print("Testing Two Body Energy Conservation...")
    # Circular orbit at 7000 km from Earth center
    r0 = 7000.0
    v0 = math.sqrt(MU_EARTH / r0)

    state = [r0, 0, 0, 0, v0, 0]

    dt = 10.0  # seconds
    t = 0.0

    initial_energy = orbital_energy(state)

    for _ in range(1000):
        state = rk4(two_body, t, state, dt)
        t += dt

    final_energy = orbital_energy(state)

    print(f"Init: {initial_energy}, Final: {final_energy}")
    assert math.isclose(initial_energy,
                        final_energy,
                        rel_tol=1e-5)
    print("PASS")

def test_solar_sail_sim_conservation():
    from lincore.solar_sail_sim import derivative
    
    print("Testing Solar Sail Sim Energy Conservation...")
    initial_state = [7000,0,0, 0,7.546,0, 1,0,0,0, 0,0,0]
    mass = 100
    sail_area = 20
    reflectivity = 0.9
    sun_dir = [1,0,0]
    inertia = [[10,0,0],[0,15,0],[0,0,20]]
    dt = 10.0
    steps = 100
    state = initial_state.copy()
    E0 = specific_energy(state)
    for i in range(steps):
        state = rk4(derivative, i*dt, state, dt, mass, sail_area, reflectivity, sun_dir, inertia)
    
    Ef = specific_energy(state)
    print(f"Init: {E0}, Final: {Ef}")
    assert abs(Ef-E0) < 1e-3
    print("PASS")

if __name__ == "__main__":
    test_energy_conservation_two_body()
    test_solar_sail_sim_conservation()
