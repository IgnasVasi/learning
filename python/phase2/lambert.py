import numpy as np
from roots import bisection

MU = 3.986e14
R_EARTH = 6.371e6


r1 = R_EARTH + 400e3          # LEO

def stumpff_C(z):
    if z>0:
        return (1-np.cos(np.sqrt(z)))/z
    if z<0:
        return (np.cosh(np.sqrt(-z))-1)/(-z)
    return 1/2

def stumpff_S(z):
    if z >0:
        s = np.sqrt(z)
        return (s - np.sin(s))/s**3
    if z < 0:
        s = np.sqrt(-z)
        return (np.sinh(s) - s) / s**3
    return 1/6

def lambert(r1_vec, r2_vec, dt, mu):
    r1 = np.linalg.norm(r1_vec)
    r2 = np.linalg.norm(r2_vec)

    dtheta = np.arccos(np.clip(np.dot(r1_vec, r2_vec)/(r1*r2), -1, 1))
    cross = r1_vec[0] * r2_vec[1] - r1_vec[1]*r2_vec[0]
    if cross < 0:
        dtheta = 2*np.pi-dtheta

    A = np.sin(dtheta) * np.sqrt(r1 * r2/(1-np.cos(dtheta)))

    def y(z):
        return r1 + r2 + A* (z * stumpff_S(z) - 1)/np.sqrt(stumpff_C(z))

    def time_error(z):
        yz = y(z)
        if yz < 0:
            return -1e30
        return (yz / stumpff_C(z))**1.5 * stumpff_S(z) + A * np.sqrt(yz) - np.sqrt(mu) * dt
    z, steps = bisection(time_error, -400, 4*np.pi**2 - 1e-9)


    yz = y(z)
    f = 1-yz/r1
    g = A * np.sqrt(yz/mu)
    gdot = 1 - yz / r2
    v1 = (r2_vec - f * r1_vec) / g
    v2 = (gdot * r2_vec - r1_vec) / g
    return v1, v2

if __name__ == "__main__":
    v1, v2 = lambert(np.array([r1, 0.0]), np.array([-30186.499e3, 14525.839e3]), 9000, MU)
    print(v1)