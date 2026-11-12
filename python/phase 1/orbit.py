import math
import numpy as np
import matplotlib.pyplot as plt

MU = 3.986e14          # Earth's gravitational parameter [m^3/s^2]
R_EARTH = 6.371e6      # [m]

r0 = R_EARTH + 400e3
v_circ = np.sqrt(MU / r0)



dt=1

def simulate(k):
    v = np.array([0.0, k*v_circ])
    r = np.array([r0, 0.0])
    positions = [r]
    for step in range(20000):
        d = np.linalg.norm(r)
        a = -MU/(d**2) * r/d
        v=v+a*dt
        r=r+v*dt
        positions.append(r)
        if d<=R_EARTH:
            break
    return positions
speed_factor = 0.9
positions = simulate(speed_factor)
positions = np.array(positions)
plt.gca().add_patch(plt.Circle((0, 0), R_EARTH, color="tab:blue", alpha=0.3))
plt.plot(positions[:, 0], positions[:, 1])
plt.axis("equal")
plt.savefig("orbit.png")
print("Saved orbit.png")