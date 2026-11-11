import numpy as np
import matplotlib.pyplot as plt
from orbits import run, rk4_step, energy, R_EARTH, euler_step, semi_implicit_step


states = run(rk4_step, 10, 1000)
print(energy(states[-1]))

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