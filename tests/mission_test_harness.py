import math
import matplotlib.pyplot as plt
from .solar_sail_sim import rk4, derivative, specific_energy, angular_momentum, quat_rotate
from .solar_sail_opt import propagate_trajectory, optimize_sail_orientation

# ---------------------------
# Mission Parameters
# ---------------------------
MU_EARTH = 398600.4418  # km^3/s^2
mass = 100.0             # kg
sail_area = 20.0         # m^2
reflectivity = 0.9
inertia = [[10,0,0],[0,15,0],[0,0,20]]
sun_dir = [1,0,0]        # Sun direction
dt = 10.0
steps = 2000

# Initial orbit (circular LEO)
r0 = 7000.0              # km
v0 = math.sqrt(MU_EARTH/r0)
initial_state = [r0,0,0, 0,v0,0, 1,0,0,0, 0,0,0]  # [r,v,q,ω]

# ---------------------------
# Run Full Coupled Simulation
# ---------------------------
positions, energies, angular_momenta, final_state = propagate_trajectory(
    initial_state, mass, sail_area, reflectivity, sun_dir, inertia, dt, steps
)

# ---------------------------
# Verification: NASA-grade Checks
# ---------------------------
energy_drift = energies[-1]-energies[0]
h_drift = [angular_momenta[-1][i]-angular_momenta[0][i] for i in range(3)]

print("=== NASA-Grade Verification ===")
print("Initial Energy:", energies[0])
print("Final Energy:", energies[-1])
print("Energy Drift:", energy_drift)
print("Initial Angular Momentum:", angular_momenta[0])
print("Final Angular Momentum:", angular_momenta[-1])
print("Angular Momentum Drift:", h_drift)
print("Final Position (km):", final_state[:3])
print("Final Velocity (km/s):", final_state[3:6])

# ---------------------------
# Plot Trajectory
# ---------------------------
xs = [p[0] for p in positions]
ys = [p[1] for p in positions]
plt.figure(figsize=(8,8))
plt.plot(xs, ys, label="Solar Sail Orbit")
plt.xlabel("X [km]")
plt.ylabel("Y [km]")
plt.title("NASA-Grade Solar Sail Orbit with J2 + Attitude")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()

# ---------------------------
# Additional Mission Metrics
# ---------------------------
# Compute max radial distance
radial_distances = [math.sqrt(p[0]**2 + p[1]**2 + p[2]**2) for p in positions]
print("Maximum Orbital Radius (km):", max(radial_distances))
print("Minimum Orbital Radius (km):", min(radial_distances))
print("Delta Radius:", max(radial_distances)-min(radial_distances))
