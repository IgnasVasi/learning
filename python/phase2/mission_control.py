import numpy as np
import pygame
from solar import AU, earth, venus, best_trip, transfer_arc, phase_deg, days_to_window, IDEAL_PHASE

# ===== Screen settings =====
WIDTH, HEIGHT = 1100, 750
CENTRE = (330, 375)
PX_PER_AU = 250
SKY = (86, 180, 233)            # Earth
ORANGE = (230, 159, 0)          # Venus
YELLOW = (240, 228, 66)         # spacecraft / "launch now"
PURPLE = (204, 121, 167)        # "wait for the window"
GREY = (120, 120, 140)
WHITE = (230, 230, 230)
WARPS = [2, 10, 30, 60]         # days per real second


def to_screen(pos):
    return (int(CENTRE[0] + pos[0] / AU * PX_PER_AU), int(CENTRE[1] - pos[1] / AU * PX_PER_AU))


def make_plan(now):
    """Everything the planner needs: best trip NOW and best trip at the NEXT WINDOW."""
    days, costs, best_now, cost_now = best_trip(now)
    window_day = now + days_to_window(now)
    _, _, best_win, cost_win = best_trip(window_day)
    return {
        "days": days, "costs": costs,
        "now_days": best_now, "now_cost": cost_now,
        "now_arc": transfer_arc(now, best_now, cost_now[0]),
        "win_day": window_day, "win_days": best_win, "win_cost": cost_win,
        "win_arc": transfer_arc(window_day, best_win, cost_win[0]),
    }


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mission control: Earth -> Venus")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
small = pygame.font.SysFont(None, 18)

now = 0.0                       # today's date, in days (keeps running)
warp_index = 1
mode = "cruise"                 # "cruise", "plan", "flying" or "arrived"
plan = None
scheduled_day = None            # day of an automatic launch, if one is booked
flight = None                   # the trip being flown: launch day, flight days, arc
running = True


def launch(day):
    """Find the best trip for 'day' and start flying it."""
    _, _, flight_days, cost = best_trip(day)
    return {"launch": day, "days": flight_days, "cost": cost, "arc": transfer_arc(day, flight_days, cost[0])}


while running:
    real_dt = clock.tick(60) / 1000

    # ----- 1. Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type != pygame.KEYDOWN:
            continue
        if event.key == pygame.K_PERIOD:
            warp_index = min(warp_index + 1, len(WARPS) - 1)
        if event.key == pygame.K_COMMA:
            warp_index = max(warp_index - 1, 0)

        if mode == "cruise" and event.key == pygame.K_p:          # P: stop and analyse
            plan = make_plan(now)
            mode = "plan"
        elif mode == "plan":
            if event.key == pygame.K_SPACE:                       # launch right now
                flight = launch(now)
                mode = "flying"
            elif event.key == pygame.K_w:                         # book the window
                scheduled_day = plan["win_day"]
                mode = "cruise"
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):      # back, no launch
                mode = "cruise"
        elif mode == "arrived" and event.key == pygame.K_r:       # new mission
            flight = None
            mode = "cruise"

    # ----- 2. Time moves (except while planning) -----
    if mode != "plan" and mode != "arrived":
        new_now = now + WARPS[warp_index] * real_dt
        if mode == "cruise" and scheduled_day is not None and new_now >= scheduled_day:
            new_now = scheduled_day                               # stop exactly on the window...
            flight = launch(scheduled_day)                        # ...and launch automatically
            scheduled_day = None
            mode = "flying"
        now = new_now
    if mode == "flying" and now >= flight["launch"] + flight["days"]:
        now = flight["launch"] + flight["days"]
        mode = "arrived"

    # ----- 3. Draw: Sun, orbits, planets -----
    screen.fill((10, 10, 25))
    pygame.draw.circle(screen, GREY, CENTRE, PX_PER_AU, 1)
    pygame.draw.circle(screen, GREY, CENTRE, int(0.723332 * PX_PER_AU), 1)
    pygame.draw.circle(screen, (255, 230, 150), CENTRE, 10)

    if mode == "plan":
        pygame.draw.lines(screen, YELLOW, False, [to_screen(p) for p in plan["now_arc"][:, :2]], 2)
        pygame.draw.lines(screen, PURPLE, False, [to_screen(p) for p in plan["win_arc"][:, :2]], 2)
        # where Earth will be on window day, and where Venus will be on each arrival day (rings = future)
        e_win, _ = earth(plan["win_day"])
        v_arr_now, _ = venus(now + plan["now_days"])
        v_arr_win, _ = venus(plan["win_day"] + plan["win_days"])
        for pos, colour, label in [(e_win, PURPLE, "Earth on window day"),
                                   (v_arr_now, YELLOW, "Venus at arrival (now)"),
                                   (v_arr_win, PURPLE, "Venus at arrival (window)")]:
            p = to_screen(pos)
            pygame.draw.circle(screen, colour, p, 8, 2)
            screen.blit(small.render(label, True, colour), (p[0] + 10, p[1] + 6))

    if flight is not None:
        arc = flight["arc"]
        pygame.draw.lines(screen, YELLOW, False, [to_screen(p) for p in arc[:, :2]], 1)
        fraction = min((now - flight["launch"]) / flight["days"], 1.0)
        i = int(fraction * (len(arc) - 1))
        pygame.draw.circle(screen, YELLOW, to_screen(arc[i, :2]), 5)

    e_pos, _ = earth(now)
    v_pos, _ = venus(now)
    pygame.draw.circle(screen, SKY, to_screen(e_pos), 7)
    pygame.draw.circle(screen, ORANGE, to_screen(v_pos), 7)
    screen.blit(small.render("Earth", True, SKY), (to_screen(e_pos)[0] + 10, to_screen(e_pos)[1]))
    screen.blit(small.render("Venus", True, ORANGE), (to_screen(v_pos)[0] + 10, to_screen(v_pos)[1]))

    # ----- 4. Draw: text -----
    lines = [
        f"Day {now:7.1f}     Time: {WARPS[warp_index]} days/s     Mode: {mode.upper()}",
        f"Venus angle: {phase_deg(now):+.0f} deg   (window at {IDEAL_PHASE})",
    ]
    if scheduled_day is not None:
        lines.append(f"AUTO-LAUNCH booked: in {scheduled_day - now:.0f} days")
    if mode == "cruise":
        lines += ["", "P = stop and plan a launch", ", . = time speed"]
    if mode == "flying":
        lines += ["", f"In flight: day {now - flight['launch']:.0f} of {flight['days']}",
                  f"Trip cost: {flight['cost'][1] / 1000:.2f} km/s"]
    if mode == "arrived":
        lines += ["", f"ARRIVED at Venus after {flight['days']} days!",
                  f"Trip cost: {flight['cost'][1] / 1000:.2f} km/s", "R = new mission"]
    if mode == "plan":
        now_total = plan["now_cost"][1] / 1000
        win_total = plan["win_cost"][1] / 1000
        lines += [
            "",
            f"LAUNCH NOW (yellow):  {plan['now_days']} days,  {now_total:.2f} km/s",
            f"   departure {plan['now_cost'][2] / 1000:.2f} + arrival {plan['now_cost'][3] / 1000:.2f}",
            f"WAIT FOR WINDOW (purple):  in {plan['win_day'] - now:.0f} days",
            f"   {plan['win_days']} days,  {win_total:.2f} km/s",
            f"Waiting saves {now_total - win_total:.2f} km/s",
            "",
            "SPACE = launch now   W = auto-launch at window",
            "P = back without launching",
        ]
    for k, text in enumerate(lines):
        screen.blit(font.render(text, True, WHITE), (700, 40 + 24 * k))

    # ----- 5. Draw: price graph for "launch now" (plan mode) -----
    if mode == "plan":
        gx, gy, gw, gh = 700, 470, 360, 200
        pygame.draw.rect(screen, GREY, (gx, gy, gw, gh), 1)
        screen.blit(small.render("launch-now cost [km/s, 0-20] vs flight time [60-400 days]", True, WHITE), (gx, gy - 18))

        def graph_point(day, dv):
            return (int(gx + (day - 60) / 340 * gw), int(gy + gh - min(dv, 20) / 20 * gh))

        pts = [graph_point(d, c) for d, c in zip(plan["days"], plan["costs"]) if np.isfinite(c)]
        if len(pts) > 1:
            pygame.draw.lines(screen, WHITE, False, pts, 1)
        pygame.draw.circle(screen, YELLOW, graph_point(plan["now_days"], plan["now_cost"][1] / 1000), 5)

    pygame.display.flip()

pygame.quit()