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

def semi_implicit_step(state, dt):
    state = state.copy()
    rates = deriv(state)
    state[2:] = state[2:] + rates[2:]*dt
    state[:2] = state[:2] + state[2:]*dt
    return state

def rk4_step(state, dt):
    k1 = deriv(state)
    k2 = deriv(state + k1 * dt/2)
    k3 = deriv(state + k2 * dt/2)
    k4 = deriv(state + k3 * dt)
    new_state = state + dt/6 * (k1+2*k2+2*k3+k4)
    return new_state

def run (step_function, dt, n_steps):
    state = np.array([r0, 0.0, 0.0, v_circ])
    states = [state]
    for i in range(n_steps):
        state = step_function(state, dt)
        states.append(state)
    return np.array(states)

DT = 10
N = 5000

methods = [
    ("Explicit Euler", euler_step),
    ("Semi-implicit Euler", semi_implicit_step),
    ("RK4", rk4_step),
]

plt.figure(figsize=(12, 5))          # one wide image (width, height in inches)

for name, step in methods:
    states = run(step, DT, N)

    E0 = energy(states[0])
    drift = []
    for s in states:
        drift.append(abs((energy(s) - E0) / E0))
    print(f"{name}: max energy error {max(drift):.1e}")

    plt.subplot(1, 2, 1)             # left panel: orbits
    plt.plot(states[:, 0], states[:, 1], label=name)

    plt.subplot(1, 2, 2)             # right panel: energy
    plt.semilogy(drift, label=name)

# finishing touches, done once after the loop
plt.subplot(1, 2, 1)
plt.gca().add_patch(plt.Circle((0, 0), R_EARTH, color="tab:blue", alpha=0.3))
plt.axis("equal")
plt.title("Orbits")
plt.legend()

plt.subplot(1, 2, 2)
plt.xlabel("Step")
plt.ylabel("Relative energy error")
plt.title("Energy drift")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("comparison.png")