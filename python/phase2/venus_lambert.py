import numpy as np
import matplotlib.pyplot as plt
from lambert import lambert

MU_SUN = 1.32712e20
AU = 1.495978707e11
DAY = 86400

r_earth = 1.0 * AU
r_venus = 0.723332 * AU
v_earth = np.sqrt(MU_SUN / r_earth)        # Earth's orbital speed
v_venus = np.sqrt(MU_SUN / r_venus)        # Venus's orbital speed
T_venus = 2 * np.pi * np.sqrt(r_venus**3 / MU_SUN)

earth_pos = np.array([r_earth, 0.0])       # Earth at launch
earth_vel = np.array([0.0, v_earth])       # moving "up"

def venus_at(t, start_deg):
    angle = np.radians(start_deg) + 2 * np.pi * t/ T_venus
    pos = r_venus * np.array([np.cos(angle), np.sin(angle)])
    vel = v_venus * np.array([-np.sin(angle), np.cos(angle)])
    return pos, vel

for start_deg in [-54, 0]:
    days_list = []
    dv_list = []
    for days in range(60,401,5):
        venus_pos, venus_vel = venus_at(days * DAY, start_deg)
        v1, v2 = lambert(earth_pos,venus_pos,days * DAY, MU_SUN)
        dv_depart = np.linalg.norm(v1 - earth_vel)
        days_list.append(days)
        dv_list.append(dv_depart / 1000)
    best = np.argmin(dv_list)
    print(f"Venus at {start_deg}°: best = {days_list[best]} days, {dv_list[best]:.2f} km/s")
    plt.plot(days_list, dv_list, label=f"Venus at {start_deg}° at launch")                   # blank 4: a label with start_deg in it

plt.ylim(0, 20)
plt.xlabel("Flight time [days]")
plt.ylabel("Departure Δv [km/s]")
plt.legend()
plt.grid(True)
plt.savefig("venus_lambert.png")