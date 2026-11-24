import time
import numpy as np
import matplotlib.pyplot as plt
from solar import trip_cost

# ===== 1. The grid of trips to try  [Read] =====
launch_days = np.arange(0, 1201, 4)      # x axis: launch date
flight_days = np.arange(60, 401, 4)      # y axis: flight time
dv = np.full((len(flight_days), len(launch_days)), np.nan)         # BLANK 1: rows = flight times (y), columns = launch days (x)

start = time.time()
for i, launch in enumerate(launch_days):
    for j, flight in enumerate(flight_days):
        result = trip_cost(launch, flight)
        if result is not None:
            dv[j, i] = result[1]/1000
print(f"{dv.size} trips in {time.time() - start:.1f} s")

j_best, i_best = np.unravel_index(np.nanargmin(dv), dv.shape)
print(f"Cheapest: launch day {launch_days[i_best]}, {flight_days[j_best]} days, {dv[j_best, i_best]:.2f} km/s")

fig, ax = plt.subplots(figsize=(10, 6))
levels = np.arange(5, 30.1, 1)
filled = ax.contourf(launch_days, flight_days, np.clip(dv, None, 30), levels=levels, cmap="viridis_r", extend="max")
lines = ax.contour(launch_days, flight_days, dv, levels=[6, 8, 12, 20], colors="white", linewidths=0.8)
ax.clabel(lines, fmt="%.0f km/s", fontsize=8)
fig.colorbar(filled, label="total Δv [km/s]")
ax.plot(launch_days[i_best], flight_days[j_best], marker="*", color="#E69F00", markersize=18,
        markeredgecolor="black", label=f"cheapest: {dv[j_best, i_best]:.2f} km/s")
ax.set_xlabel("launch day")
ax.set_ylabel("flight time [days]")
ax.set_title("Porkchop plot: Earth → Venus")
ax.legend(loc="upper right")
plt.savefig("porkchop.png", dpi=120, bbox_inches="tight")
print("saved porkchop.png")