import numpy as np

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


if __name__ == "__main__":
    states = run(rk4_step, 10, 100)
    print("Self-test OK, final altitude [km]:",
          (np.linalg.norm(states[-1, :2]) - R_EARTH) / 1000)