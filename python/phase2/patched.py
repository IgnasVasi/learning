import time
import numpy as np
import matplotlib.pyplot as plt
from lambert import lambert
from orbits import propagate
from solar import earth, venus, MU_SUN, AU, DAY

MU_VENUS = 3.24859e14                # Venus's gravity (G*M), m^3/s^2
R_FLYBY = 6051.8e3 + 300e3           # closest allowed pass: Venus radius + 300 km
BODIES = {"earth": earth, "venus": venus}

cache = {}

def leg(start, end, day, flight_days):
    key = (start, end, day, flight_days)
    if key in cache:
        return cache[key]
    r1, v1_planet = BODIES[start](day)
    r2, v2_planet = BODIES[end](day + flight_days)
    v1, v2 = lambert(r1, r2, flight_days * DAY, MU_SUN)
    cache[key] = v1 - v1_planet, v2 - v2_planet
    return cache[key]

def flyby_check(v_in, v_out):
    v_in_len = np.linalg.norm(v_in)
    v_out_len = np.linalg.norm(v_out)
    dv = abs(v_out_len - v_in_len)
    cos_turn = np.dot(v_in, v_out) / (v_in_len * v_out_len)
    turn = np.degrees(np.arccos(np.clip(cos_turn, -1, 1)))
    e = 1 + R_FLYBY * v_in_len**2 / MU_VENUS                
    max_turn = np.degrees(2 * np.arcsin(1 / e))   
    return dv, turn, max_turn

test = flyby_check(np.array([5000.0, 0.0]), np.array([0.0, 5000.0])) 
print(f"test: engine {test[0]:.0f} m/s, turn {test[1]:.1f} deg, max turn {test[2]:.1f} deg")

start = time.time()
best = None
for launch in range(380, 481, 4):
    for t1 in range(120,221,4):
        launch_vinf, v_in = leg("earth", "venus", launch, t1)
        for t2 in range(250, 401, 4):
            v_out, return_vinf = leg("venus", "earth", launch + t1, t2)
            if not np.all(np.isfinite(np.concatenate([v_in, v_out, return_vinf]))):
                continue
            dv, turn, max_turn = flyby_check(v_in, v_out)
            if dv > 50 or turn > max_turn or np.linalg.norm(launch_vinf) > 3000:
                continue                                     # not free, can't turn that much, or too costly to launch
            gain = np.linalg.norm(return_vinf)
            if best is None or gain > best[0]:
                best = (gain, launch, t1, t2, np.linalg.norm(launch_vinf), np.linalg.norm(v_in), dv, turn, max_turn)
print(f"search took {time.time() - start:.1f} s")

gain, launch, t1, t2, launch_v, venus_v, dv, turn, max_turn = best
print(f"Launch day {launch}: leave Earth at v_inf {launch_v / 1000:.2f} km/s")
print(f"Day {launch + t1}: Venus flyby at v_inf {venus_v / 1000:.2f} km/s, turn {turn:.0f} deg (max {max_turn:.0f}), engine {dv:.0f} m/s")
print(f"Day {launch + t1 + t2}: back at Earth with v_inf {gain / 1000:.2f} km/s")
print(f"search took {time.time() - start:.1f} s, Lambert solves: {len(cache)}")
# ===== 4. Plot  [Paste] =====
r_e, v_e = earth(launch)
launch_vinf, _ = leg("earth", "venus", launch, t1)
arc1 = propagate(np.concatenate([r_e, v_e + launch_vinf]), t1 * DAY / 500, 500, mu=MU_SUN)
r_v, v_v = venus(launch + t1)
v_out, _ = leg("venus", "earth", launch + t1, t2)
arc2 = propagate(np.concatenate([r_v, v_v + v_out]), t2 * DAY / 500, 500, mu=MU_SUN)
r_back, _ = earth(launch + t1 + t2)

fig, ax = plt.subplots(figsize=(7, 7))
angles = np.linspace(0, 2 * np.pi, 300)
for radius in [1.0, 0.723332]:
    ax.plot(radius * np.cos(angles), radius * np.sin(angles), color="#999999", linewidth=0.8)
ax.plot(arc1[:, 0] / AU, arc1[:, 1] / AU, color="#0072B2", linewidth=2, label=f"leg 1: Earth → Venus ({t1} d)")
ax.plot(arc2[:, 0] / AU, arc2[:, 1] / AU, color="#E69F00", linewidth=2, linestyle="--", label=f"leg 2: Venus → Earth ({t2} d)")
ax.plot(0, 0, marker="o", color="#F0E442", markersize=14, markeredgecolor="black")
ax.plot(r_e[0] / AU, r_e[1] / AU, marker="o", color="#56B4E9", markersize=10, markeredgecolor="black", linestyle="none", label=f"launch, day {launch}")
ax.plot(r_v[0] / AU, r_v[1] / AU, marker="s", color="#CC79A7", markersize=10, markeredgecolor="black", linestyle="none", label=f"Venus flyby, day {launch + t1}")
ax.plot(r_back[0] / AU, r_back[1] / AU, marker="^", color="#56B4E9", markersize=11, markeredgecolor="black", linestyle="none", label=f"back at Earth, day {launch + t1 + t2}")
ax.set_aspect("equal")
ax.set_xlabel("x [AU]")
ax.set_ylabel("y [AU]")
ax.set_title(f"Earth → Venus → Earth: launch {launch_v / 1000:.2f} km/s, return {gain / 1000:.2f} km/s")
ax.legend(loc="lower left", fontsize=8)
plt.savefig("eve.png", dpi=120, bbox_inches="tight")
print("saved eve.png")          