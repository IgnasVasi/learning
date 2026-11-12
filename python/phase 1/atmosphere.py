import math
import matplotlib.pyplot as plt
H = []
T = []
P = []
Rho = []

T0 = 288.15      # sea-level temperature [K]
P0 = 101325      # sea-level pressure [Pa]
L = 0.0065       # temperature lapse rate [K/m]
R = 287.05       # gas constant for air [J/(kg·K)]

def isa(h):
    t = T0 - L * h
    p = P0 * (t / T0)**5.2559
    rho = p / (R * t)
    return t, p, rho

for h in range(0,11001, 100):
    t, p, rho = isa(h)
    T.append(t)
    P.append(p)
    Rho.append(rho)
    H.append(h)
plt.subplot(1,3,1)
plt.plot(T, H)
plt.xlabel("Temperature [K]")
plt.ylabel("Altitude [m]")
plt.grid(True)

plt.subplot(1,3,2)
plt.plot(P, H)
plt.xlabel("Pressure [Pa]")
plt.ylabel("Altitude [m]")
plt.grid(True)

plt.subplot(1,3,3)
plt.plot(Rho, H)
plt.xlabel("Density [kg/m3]")
plt.ylabel("Altitude [m]")
plt.grid(True)
plt.tight_layout()  
plt.savefig("atmosphere.png")
plt.show()
#yeah baby