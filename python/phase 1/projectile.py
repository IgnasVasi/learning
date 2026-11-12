import math
import matplotlib.pyplot as plt

# Constants
G = 9.81          # gravity [m/s^2]
RHO_AIR = 1.225   # air density at sea level [kg/m^3]

# Football
M = 0.43                          # mass [kg]
D_BALL = 0.22                     # diameter [m]
CD = 0.25                         # drag coefficient
A = math.pi * (D_BALL / 2)**2     # frontal area [m^2]

# Launch
V0 = 30                           # launch speed [m/s]
THETA = math.radians(45)          # launch angle
DT = 0.01                         # time step [s]


def simulate(with_drag):
    """Return lists of x and y positions until the ball hits the ground."""
    x, y = 0.0, 0.0
    vx = V0 * math.cos(THETA)
    vy = V0 * math.sin(THETA)
    xs, ys = [x], [y]

    while y >= 0:
        v = math.sqrt(vx**2 + vy**2)
        if with_drag:
            D = 0.5 * RHO_AIR * CD * A * v**2   # drag force [N]
        else:
            D = 0
        ax = -(D / M) * (vx / v)
        ay = -G - (D / M) * (vy / v)
        vx += ax * DT
        vy += ay * DT
        x += vx * DT
        y += vy * DT
        xs.append(x)
        ys.append(y)

    return xs, ys


xs_vac, ys_vac = simulate(with_drag=False)
xs_drag, ys_drag = simulate(with_drag=True)

print(f"No drag:    range {xs_vac[-1]:.1f} m, max height {max(ys_vac):.1f} m")
print(f"With drag:  range {xs_drag[-1]:.1f} m, max height {max(ys_drag):.1f} m")
print(f"Analytical no-drag range: {V0**2 / G:.1f} m")

plt.plot(xs_vac, ys_vac, label="no drag")
plt.plot(xs_drag, ys_drag, label="with drag")
plt.xlabel("Distance [m]")
plt.ylabel("Height [m]")
plt.title("Football kicked at 30 m/s, 45°")
plt.axis("equal")
plt.legend()
plt.grid(True)
plt.savefig("projectile.png")
plt.show()