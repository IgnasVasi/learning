import numpy as np
from orbits import propagate, burn, orbit_elements
import matplotlib.pyplot as plt

MU = 3.986e14
R_EARTH = 6.371e6


r1 = R_EARTH + 400e3          # LEO
r2 = R_EARTH + 35786e3        # GEO

def vis_viva(r, a):
    return np.sqrt(MU*(2/r-1/a))

a_transfer = (r1+r2)/2
v_circ1=vis_viva(r1, r1)
v_perigee=vis_viva(r1, a_transfer)
v_apogee = vis_viva(r2, a_transfer)
v_circ2= vis_viva(r2,r2)

dv1=v_perigee-v_circ1
dv2=v_circ2-v_apogee
t_transfer = np.pi * np.sqrt(a_transfer**3/MU)

#print(f"Burn 1: {dv1:.0f} m/s")
#print(f"Burn 2: {dv2:.0f} m/s")
#print(f"Total:  {dv1 + dv2:.0f} m/s")
#print(f"Transfer time: {t_transfer / 3600:.2f} h")

DT = 10   # seconds per step

# 1. Start in the low circle
state = np.array([r1, 0.0, 0.0, v_circ1])

# 2. First burn, then coast up the ellipse
state = burn(state, dv1)
transfer = propagate(state, DT, int(t_transfer / DT))     # how many 10 s steps fit in t_transfer? (use int(...))

# 3. Second burn at the top, then fly one day
state = burn(transfer[-1], dv2)          # transfer[-1] = where the satellite is now
geo = propagate(state, DT, 8640)          # one day = 86400 s

# 4. Check
end_altitude = (np.linalg.norm(transfer[-1, :2]) - R_EARTH) / 1000
print(f"Altitude after transfer: {end_altitude:.0f} km")

# 5. Plot
plt.gca().add_patch(plt.Circle((0, 0), R_EARTH, color="tab:blue", alpha=0.3))
plt.plot(transfer[:, 0], transfer[:, 1], label="transfer ellipse")
plt.plot(geo[:, 0], geo[:, 1], label="GEO orbit")
plt.axis("equal")
plt.legend()
plt.savefig("hohmann.png")

from orbits import orbit_elements

print(orbit_elements(np.array([r1, 0.0, 0.0, v_circ1])))         # the LEO circle
print(orbit_elements(burn(np.array([r1, 0.0, 0.0, v_circ1]), dv1)))  # right after burn 1