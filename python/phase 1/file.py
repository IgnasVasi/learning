import numpy as np
import matplotlib.pyplot as plt
from orbits import run, rk4_step, energy, R_EARTH, euler_step, semi_implicit_step


DT = 10                  # seconds per step
N = 8640                  # how many steps in one day?

states = run(rk4_step, DT, N)

print("hours,altitude_km")
for i in range(0, len(states), 60):
    hours = i*DT/3600          # convert step number i into 
    r = states[i,:2]
    altitude_km = (np.linalg.norm(r) -R_EARTH )/1000 # altitude of row i, in km
    print(f"{hours:.3f},{altitude_km:.3f}")