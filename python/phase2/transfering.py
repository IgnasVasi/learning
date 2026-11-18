from roots import newton
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


DT = 10   # seconds per step

#making the simulation
state = np.array([r1, 0.0, 0.0, v_circ1])


state = burn(state, dv1)
n_steps = 900

transfer = propagate(state, DT, n_steps)    

#making solver

e = (r2 - r1)/(r2 + r1)
n = np.sqrt(MU/a_transfer**3)
M = n*n_steps*DT

f = lambda x: x-e*np.sin(x) - M
df = lambda x: 1-e*np.cos(x)
x = M
E, steps = newton(f, df, x)
xpoz = a_transfer * (np.cos(E) - e)/1000
ypoz = a_transfer * np.sqrt(1 - e**2) * np.sin(E)/1000
print(E)
print(f"Position from solver: {xpoz:.2f}, {ypoz:.2f} km")
x_sim = transfer[-1, 0] / 1000
y_sim = transfer[-1, 1] / 1000
print(f"Position from simulation: {x_sim:.2f}, {y_sim:.2f} km")

diff_km = np.linalg.norm(np.array([x_sim, y_sim]) - np.array([xpoz, ypoz]))
print(f"Difference: {diff_km:.6f} km")