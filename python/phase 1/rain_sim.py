import random
from rain_classes import Raindrop, Person
import matplotlib.pyplot as plt
import numpy as np

DISTANCE = 10          # how far the person walks [m]
RAIN_SPEED = 6.5       # terminal velocity of a 2 mm drop [m/s]
RATE = 200             # new drops per second, per metre of ground
SPAWN_Y = 3.0          # drops appear at this height [m]
X_MIN, X_MAX = -1, 12  # rain falls over this stretch [m]
DT = 0.01              # time step [s]
windspeed = -2


def theory(v, w=0):
    top = RATE * 0.3 * DISTANCE / v
    side = (RATE / RAIN_SPEED) * 1.8 * abs(v - w) * DISTANCE / v
    return top + side

def add_new_drops(drops, wspeed=0):
    n_new = int(RATE * (X_MAX - X_MIN)*DT)
    for _ in range(n_new):
        drift = wspeed * SPAWN_Y / RAIN_SPEED
        x = random.uniform(X_MIN - drift, X_MAX - drift) 
        drops.append(Raindrop(x = x, y = SPAWN_Y, speed= RAIN_SPEED))

def walk(speed, wspeed=0):
    person = Person(speed)
    drops = []
    hits = 0

    for _ in range(int(0.6/DT)):
        add_new_drops(drops, wspeed)
        survivors = []
        for drop in drops:
            drop.step(DT, wspeed)
            if not drop.on_ground():
                survivors.append(drop)
        drops = survivors

    while person.x < DISTANCE:
        add_new_drops(drops, wspeed)
        person.step(DT)
        survivors = []
        for drop in drops:
            drop.step(DT, wspeed)
            if person.is_hit(drop):
                hits += 1
            elif not drop.on_ground():
                survivors.append(drop)
        drops = survivors
    return hits

if __name__ == "__main__":
    speeds = [1, 2, 3, 4, 5, 6, 7, 8]
    avg_hits = []
    for v in speeds:
        total = 0
        for i in range(10):
           total += walk(v, windspeed)            
        avg_hits.append(total/10)       

    # --- Theory: a smooth curve ---
    v_smooth = np.linspace(1, 8, 100)    # 100 speeds evenly spaced from 1 to 8

    plt.plot(v_smooth, theory(v_smooth, windspeed), label="theory")
    plt.plot(speeds, avg_hits, "o", label="simulation")    # "o" = dots, no line
    plt.xlabel("Speed [m/s]")
    plt.ylabel("Raindrops hit")
    plt.title("Walk or run in the rain? (10 m, vertical rain)")
    plt.legend()
    plt.grid(True)
    plt.savefig("rain_result.png")
    plt.show()
