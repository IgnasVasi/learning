import math

g =9.81

h=float(input("Drop height meters: "))
t = math.sqrt(2*h/g)
v=g/t
print(f"time to fall:{t:.2f} s")
print(f"impact velocity: {v:.2f} m/s ({v*3.6:.1f} km/s)")
print("\nHeight Time")
for height in range(10,101,10):
    t_h = math.sqrt(2*height/g)
    print(f"{height:4d} m {t_h:.2f} s")