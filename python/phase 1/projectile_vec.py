import numpy as np
import matplotlib.pyplot as plt

G = 9.81
DT = 0.01

r = np.array([0.0, 0.0])                         # position [m]
v = np.array([30 * np.cos(np.radians(45)),
              30 * np.sin(np.radians(45))])      # velocity [m/s]
g_vec = np.array([0.0, -G])                      # gravity as a vector

positions = [r]
while r[1] >= 0:                 # r[1] is the y component
    v = v + g_vec * DT
    r = r + v * DT
    positions.append(r)

positions = np.array(positions)  # list of vectors -> one 2D table
print(f"Range: {r[0]:.1f} m")

plt.plot(positions[:, 0], positions[:, 1])   # all x's, all y's
plt.axis("equal")
plt.grid(True)
plt.show()