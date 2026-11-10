import math
import matplotlib.pyplot as plt

# Constants
G = 9.81            # gravity [m/s^2]
RHO_AIR = 1.225     # air density at sea level [kg/m^3]
RHO_WATER = 1000    # [kg/m^3]
CD = 0.5            # drag coefficient of a sphere

# Raindrop
d = 0.002                                   # diameter [m]
r = d / 2
m = RHO_WATER * 4/3 * math.pi * r**3        # mass [kg]
A = math.pi * r**2                          # frontal area [m^2]

# Simulation
dt = 0.01       # time step [s]
t = 0.0
v = 0.0         # downward speed [m/s]

times = [t]
speeds = [v]

while t < 5:
    drag = 0.5 * RHO_AIR * CD * A * v**2    # drag force [N]
    a = G - drag / m                        # Newton: a = F/m
    v += a * dt
    t += dt
    times.append(t)
    speeds.append(v)

# Analytical check: drag = weight  ->  v = sqrt(2mg / (rho Cd A))
v_terminal = math.sqrt(2 * m * G / (RHO_AIR * CD * A))
print(f"Simulated speed after 5 s: {v:.2f} m/s")
print(f"Analytical terminal speed: {v_terminal:.2f} m/s")

plt.plot(times, speeds, label="simulation")
plt.axhline(v_terminal, linestyle="--", color="gray", label="terminal velocity")
plt.xlabel("Time [s]")
plt.ylabel("Fall speed [m/s]")
plt.legend()
plt.grid(True)
plt.savefig("raindrop.png")
plt.show()