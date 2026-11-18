import numpy as np
import matplotlib.pylab as plt

# ===== The planet =====
MU_PLANET = 3.986e14                  # Earth [m^3/s^2]
R_PLANET = 6.371e6                    # [m]
V_PLANET = np.array([29.78e3, 0.0])   # moving right at Earth's orbital speed [m/s]


def planet_position(t):
    """The planet moves in a straight line and is at (0, 0) at t = 0."""
    return V_PLANET * t

def deriv(t, state):
    r = state[:2]
    v = state[2:]
    d_vec = r-planet_position(t)
    d = np.linalg.norm(d_vec)
    a = -(MU_PLANET/d**2) * (d_vec/d)
    return np.concatenate([v, a])

def rk4_step(f, t, state, dt):
    k1 = f(t, state)
    k2 = f(t + dt/2, state +k1 *dt/2)
    k3 = f(t + dt/2, state + k2 *dt/2)
    k4 = f(t + dt, state + k3 *dt)
    return state + dt/6 * (k1+2*k2+2*k3+k4)

def energy(state, t):
    r = state[:2] - planet_position(t)
    v = state[2:] - V_PLANET
    return 0.5*np.dot(v,v) - MU_PLANET/np.linalg.norm(r)

def flyby(b, v_inf = 5e3, start_dist = 5e8, dt = 20):
    t = -start_dist/v_inf
    r = planet_position(t) + np.array([b, -start_dist])
    v = V_PLANET + np.array([0.0, v_inf])
    state = np.concatenate([r, v])
    crashed = False
    time = [t]
    states = [state]
    for i in range(int(2*start_dist/v_inf/dt)):
        state = rk4_step(deriv, t, state, dt)
        t = t+dt
        time.append(t)
        states.append(state)
        if np.linalg.norm(state[:2] - planet_position(t)) < R_PLANET:
            crashed = True
            break
    return np.array(time), np.array(states), crashed

b = []
speeds = []
for i in range (-60, 60, 2):
    j= float(i)*10e5
    times, states, crashed = flyby(j)
    if crashed:
        continue
    else:
        b.append(j)
        speed_before = np.linalg.norm(states[0, 2:])
        speed_after = np.linalg.norm(states[-1, 2:])
        speeds.append(speed_after-speed_before)

# b = -20e6                                  # 20 000 km, behind the planet (negative = behind)
# times, states = flyby(b)


# print(f"Speed before: {speed_before / 1000:.2f} km/s")
# print(f"Speed after:  {speed_after / 1000:.2f} km/s")
# print(f"Free speed-up: {(speed_after - speed_before) / 1000:+.2f} km/s")

# energys = []
# for t, state in zip(times, states):
#     energ = energy(state, t)
#     energys.append(energ)
#print(f"first {energys[0]:.0f} last energy {energys[-1]:.0f}")
# Path as seen FROM the planet
# rel = states[:, :2] - V_PLANET * times[:, None]
# plt.gca().add_patch(plt.Circle((0, 0), R_PLANET, color="tab:blue"))
# plt.plot(rel[:, 0], rel[:, 1])
# plt.gca().set_aspect("equal")
# plt.xlim(-1e8, 1e8)
# plt.ylim(-1e8, 1e8)
# plt.title("Flyby, seen from the planet")
# plt.savefig("flyby.png")


plt.plot(b, speeds)
plt.show()