import numpy as np
import matplotlib.pyplot as plt
from orbits import propagate

MU_SUN = 1.32712e20
AU = 1.495978707e11
DAY = 86400
r_earth = 1.0 * AU
r_venus = 0.723332 * AU


def vis_viva(r, a):
    return np.sqrt(MU_SUN * (2 / r - 1 / a))


def burn(state, dv):
    r = state[:2]
    v = state[2:]
    return np.concatenate([r, v + dv * v / np.linalg.norm(v)])

# ===== PART A: the transfer =====
a_transfer = (r_earth+r_venus)/2                    # the ellipse touching both orbits
v_earth = vis_viva(r_earth, r_earth)
v_depart = vis_viva(r_earth, a_transfer)                      # speed needed at Earth's distance, on the ellipse
dv1 = v_depart-v_earth                           # should come out NEGATIVE
t_transfer = np.pi * np.sqrt(a_transfer**3/MU_SUN)                    # half the ellipse's period, like in hohmann.py

print(f"Burn: {dv1:.0f} m/s,  flight time: {t_transfer / DAY:.1f} days")

# ===== PART B: the launch window =====
T_venus = 2 * np.pi * np.sqrt(r_venus**3 / MU_SUN)    # Venus's year [s]
venus_moves_deg = 360 * t_transfer / T_venus          # how far Venus moves during the flight
phase_deg = 180-venus_moves_deg                                       # where Venus must be at launch
print(f"Venus must be at {phase_deg:.1f}° at launch")


def venus_position(t, start_deg):
    """Where Venus is, t seconds after launch, if it started at start_deg."""
    angle = np.radians(start_deg) + 2 * np.pi * t / T_venus
    return r_venus * np.array([np.cos(angle), np.sin(angle)])


# ===== PART C: fly it =====
DT = 3600                                           # 1 hour per step
state = np.array([r_earth, 0.0, 0.0, v_earth])      # spacecraft at Earth, moving with Earth
state = burn(state, dv1)
n_steps = int(t_transfer / DT)
flight = propagate(state, DT, n_steps, mu=MU_SUN)

venus_at_arrival = venus_position(n_steps * DT, phase_deg)
miss_km = np.linalg.norm(flight[-1, :2] - venus_at_arrival) / 1000                                       # distance spacecraft ↔ Venus at the end, in km
print(f"Missed Venus by {miss_km:.0f} km")

# ===== PART D: plot =====
ax = plt.gca()
ax.add_patch(plt.Circle((0, 0), r_earth, fill=False, linestyle="--", color="tab:blue"))
ax.add_patch(plt.Circle((0, 0), r_venus, fill=False, linestyle="--", color="tab:orange"))
plt.plot(0, 0, "o", color="gold", markersize=12, label="Sun")
plt.plot(flight[:, 0], flight[:, 1], color="black", label="spacecraft")
plt.plot(*venus_at_arrival, "o", color="tab:orange", label="Venus at arrival")
plt.axis("equal")
plt.legend()
plt.savefig("venus.png")