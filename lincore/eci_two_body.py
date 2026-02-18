import math

# ---------------------------
# Constants
# ---------------------------
MU_EARTH = 398600.4418  # km^3 / s^2

# ---------------------------
# Vector operations
# ---------------------------
def norm(v):
    return math.sqrt(sum(x*x for x in v))

def cross(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

def dot(a, b):
    return sum(a[i]*b[i] for i in range(3))

# ---------------------------
# Two-body dynamics
# ---------------------------
def two_body(t, state):
    """
    state = [x, y, z, vx, vy, vz]
    returns derivative: [vx, vy, vz, ax, ay, az]
    """
    x, y, z, vx, vy, vz = state
    r = math.sqrt(x*x + y*y + z*z)
    
    ax = -MU_EARTH * x / r**3
    ay = -MU_EARTH * y / r**3
    az = -MU_EARTH * z / r**3

    return [vx, vy, vz, ax, ay, az]

# ---------------------------
# RK4 integrator
# ---------------------------
def rk4(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + dt/2, [y[i] + dt*k1[i]/2 for i in range(len(y))])
    k3 = f(t + dt/2, [y[i] + dt*k2[i]/2 for i in range(len(y))])
    k4 = f(t + dt,   [y[i] + dt*k3[i]   for i in range(len(y))])

    return [
        y[i] + dt/6 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        for i in range(len(y))
    ]

# ---------------------------
# Invariants
# ---------------------------
def specific_energy(state):
    r_vec = state[:3]
    v_vec = state[3:]
    r = norm(r_vec)
    v2 = dot(v_vec, v_vec)
    return 0.5*v2 - MU_EARTH/r

def angular_momentum(state):
    r_vec = state[:3]
    v_vec = state[3:]
    return cross(r_vec, v_vec)

# ---------------------------
# Simulation
# ---------------------------
def simulate_orbit():
    # Initial circular orbit: 7000 km radius
    r0 = 7000.0
    v0 = math.sqrt(MU_EARTH / r0)

    state = [r0, 0, 0, 0, v0, 0]  # [x, y, z, vx, vy, vz]
    dt = 10.0  # seconds
    t = 0.0
    steps = 1000

    initial_energy = specific_energy(state)
    h_vec = angular_momentum(state)
    
    print(f"Initial Energy: {initial_energy:.6f} km^2/s^2")
    print(f"Initial Angular Momentum: {h_vec}")

    for _ in range(steps):
        state = rk4(two_body, t, state, dt)
        t += dt

    final_energy = specific_energy(state)
    final_h_vec = angular_momentum(state)

    print(f"Final Energy: {final_energy:.6f} km^2/s^2")
    print(f"Final Angular Momentum: {final_h_vec}")
    print(f"Final Position: {state[:3]}")
    print(f"Final Velocity: {state[3:]}")

    energy_error = abs(final_energy - initial_energy)
    print(f"Energy Drift: {energy_error:e}")

# ---------------------------
# Run Simulation
# ---------------------------
if __name__ == "__main__":
    simulate_orbit()
