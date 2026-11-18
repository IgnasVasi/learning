import numpy as np

MU = 3.986e14
R_EARTH = 6.371e6
r0 = R_EARTH + 400e3
v_circ = np.sqrt(MU / r0)

def deriv(state, mu = MU):
    r = state[:2]
    v = state[2:]
    d = np.linalg.norm(r)
    a = -(mu/d**2)*(r/d)
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

def rk4_step(state, dt, mu = MU):
    k1 = deriv(state, mu)
    k2 = deriv(state + k1 * dt/2, mu)
    k3 = deriv(state + k2 * dt/2, mu)
    k4 = deriv(state + k3 * dt, mu)
    new_state = state + dt/6 * (k1+2*k2+2*k3+k4)
    return new_state

def run (step_function, dt, n_steps):
    state = np.array([r0, 0.0, 0.0, v_circ])
    states = [state]
    for i in range(n_steps):
        state = step_function(state, dt)
        states.append(state)
    return np.array(states)

def propagate(state, dt, n_steps, mu = MU):
    states = [state]
    for i in range (n_steps):
        state = rk4_step(state,dt, mu)
        states.append(state)
    return np.array(states)

def burn(state, dv):
    r = state[:2]
    v = state[2:]
    v_new = v + dv*v/np.linalg.norm(v)
    return np.concatenate([r, v_new])

def orbit_elements(state):
    """Turn [x, y, vx, vy] into orbit shape numbers."""
    r = state[:2]
    v = state[2:]
    r_len = np.linalg.norm(r)
    v_len = np.linalg.norm(v)
    energy = v_len**2/2-MU/r_len
    a =-MU/2/energy
    e_vec = ((v_len**2 - MU / r_len) * r - np.dot(r, v) * v) / MU
    e = np.linalg.norm(e_vec)                                  # length of e_vec
    omega = np.degrees(np.arctan2(e_vec[1], e_vec[0]))   # angle of e_vec, in degrees

    return {
        "a": a,
        "e": e,
        "e_vec": e_vec,
        "omega_deg": omega,
        "periapsis_alt_km": (a * (1 - e) - R_EARTH) / 1000,
        "apoapsis_alt_km": (a * (1 + e) - R_EARTH) / 1000,
        "period_h": 2 * np.pi * np.sqrt(a**3 / MU) / 3600,
    }


if __name__ == "__main__":
    states = run(rk4_step, 10, 100)
    print("Self-test OK, final altitude [km]:",
          (np.linalg.norm(states[-1, :2]) - R_EARTH) / 1000)