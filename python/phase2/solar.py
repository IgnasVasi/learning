"""Physics for the Earth -> Venus mission planner (no drawing in here)."""
import numpy as np
from lambert import lambert
from orbits import propagate

MU_SUN = 1.32712e20
AU = 1.495978707e11
DAY = 86400
R_EARTH_ORBIT = 1.0 * AU
R_VENUS_ORBIT = 0.723332 * AU
T_EARTH = 2 * np.pi * np.sqrt(R_EARTH_ORBIT**3 / MU_SUN)
T_VENUS = 2 * np.pi * np.sqrt(R_VENUS_ORBIT**3 / MU_SUN)
VENUS_START_DEG = 60            # where Venus is on day 0 (Earth is at 0°)
IDEAL_PHASE = -54               # Venus angle relative to Earth for a Hohmann launch


def planet(radius, period, start_deg, day):
    """Position and velocity of a planet on a circular orbit on a given day."""
    angle = np.radians(start_deg) + 2 * np.pi * day * DAY / period
    speed = np.sqrt(MU_SUN / radius)
    pos = radius * np.array([np.cos(angle), np.sin(angle)])
    vel = speed * np.array([-np.sin(angle), np.cos(angle)])
    return pos, vel


def earth(day):
    return planet(R_EARTH_ORBIT, T_EARTH, 0, day)


def venus(day):
    return planet(R_VENUS_ORBIT, T_VENUS, VENUS_START_DEG, day)


def trip_cost(launch_day, flight_days):
    """Lambert for one trip. Returns (v1, total dv, departure dv, arrival dv), or None if impossible."""
    r_e, v_e = earth(launch_day)
    r_v, v_v = venus(launch_day + flight_days)
    v1, v2 = lambert(r_e, r_v, flight_days * DAY, MU_SUN)
    dv_dep = np.linalg.norm(v1 - v_e)
    dv_arr = np.linalg.norm(v2 - v_v)
    if not np.isfinite(dv_dep + dv_arr):
        return None
    return v1, dv_dep + dv_arr, dv_dep, dv_arr


def best_trip(launch_day):
    """Try flight times from 60 to 400 days. Returns (all flight times, all costs in km/s, best flight time, best cost tuple)."""
    days = np.arange(60, 401, 2)
    costs = []
    for d in days:
        result = trip_cost(launch_day, d)
        costs.append(result[1] / 1000 if result else np.nan)
    costs = np.array(costs)
    best_days = int(days[np.nanargmin(costs)])
    return days, costs, best_days, trip_cost(launch_day, best_days)


def transfer_arc(launch_day, flight_days, v1):
    r_e, _ = earth(launch_day)
    return propagate(np.concatenate([r_e, v1]), flight_days * DAY / 300, 300, mu=MU_SUN)


def phase_deg(day):
    """Angle of Venus relative to Earth, between -180 and +180 degrees."""
    e, _ = earth(day)
    v, _ = venus(day)
    angle = np.degrees(np.arctan2(v[1], v[0]) - np.arctan2(e[1], e[0]))
    return (angle + 180) % 360 - 180


def days_to_window(day):
    """How many days until Venus is at the ideal angle again."""
    rate = 360 / (T_VENUS / DAY) - 360 / (T_EARTH / DAY)       # degrees per day (~0.617)
    return ((IDEAL_PHASE - phase_deg(day)) % 360) / rate


if __name__ == "__main__":
    print("window in", days_to_window(0), "days")
    days, costs, best, cost = best_trip(399)
    print("best at day 399:", best, "days,", cost[1] / 1000, "km/s")