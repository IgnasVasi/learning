import numpy as np
import matplotlib.pyplot as plt

MU = 3.986e14
R_EARTH = 6.371e6
r0 = R_EARTH + 400e3
v_circ = np.sqrt(MU / r0)

def deriv(state):
    r = state[:2]
    v = state[2:]
    d = np.linalg.norm(r)
    a = -(MU/d**2)*(r/d)
    return np.concatenate([v, a])

def energy(state):
    r = state[:2]
    v = state[2:]
    return 0.5*np.dot(v,v) - MU/np.linalg.norm(r)

def euler_step(state, dt):
    return state + deriv(state) * dt

def run (step_function, dt, n_steps):
    state = np.array([r0, 0.0, 0.0, v_circ])
    states = [state]
    for i in range(n_steps):
        state = step_function(state, dt)
        states.append(state)
    return np.array(states)

DT = 10
N = 5000

states = run(euler_step, DT, N)

E0 = energy(states[0])
drift = []

for s in states:
    drift.append(abs((energy(s)-E0)/E0))

plt.figure()
plt.gca().add_patch(plt.Circle((0, 0), R_EARTH, color="tab:blue", alpha=0.3))
plt.plot(states[:, 0], states[:, 1], label="explicit Euler")
plt.axis("equal")
plt.legend()
plt.savefig("euler_orbit.png")

plt.figure()
plt.semilogy(drift, label="explicit Euler")   # log scale on the y-axis
plt.xlabel("Step")
plt.ylabel("Relative energy error")
plt.legend()
plt.grid(True)
plt.savefig("energy_drift.png")
print(f"Final altitude: {(np.linalg.norm(states[-1, :2]) - R_EARTH) / 1000:.0f} km")