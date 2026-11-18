import numpy as np
import pygame
from orbits import rk4_step, propagate, orbit_elements, MU, R_EARTH

# ===== Settings =====
WIDTH, HEIGHT = 1000, 800
DT = 10                           # physics step [s]: never bigger than this, for accuracy
WARPS = [1, 10, 100, 1000, 5000]  # simulated seconds per real second
DV_PER_FRAME = 5.0                # m/s added per frame while a burn key is held


def to_screen(pos, scale):
    """metres (y up, Earth at centre) -> pixels (y down, centre of window)"""
    return (int(WIDTH / 2 + pos[0] / scale), int(HEIGHT / 2 - pos[1] / scale))


def burn(state, dv):
    """Add dv along the direction of motion (negative dv = retrograde)."""
    v = state[2:]
    return np.concatenate([state[:2], v + dv * v / np.linalg.norm(v)])


def predict(state):
    """Where will we go? One full orbit ahead (or 1 day if we're escaping)."""
    el = orbit_elements(state)
    horizon = el["period_h"] * 3600 if el["e"] < 1 else 86400
    n = 400
    return propagate(state, horizon / n, n)


def start_state():
    r0 = R_EARTH + 400e3
    return np.array([r0, 0.0, 0.0, np.sqrt(MU / r0)])


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbit sandbox")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

state = start_state()
scale = 60e3                    # metres per pixel (zoom)
warp_index = 2
trail = []
prediction = predict(state)
dv_used = 0.0
sim_time = 0.0
crashed = False
running = True

while running:
    real_dt = clock.tick(60) / 1000          # real seconds since last frame (~1/60)

    # ----- 1. Events: single key presses -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PERIOD:
                warp_index = min(warp_index + 1, len(WARPS) - 1)
            if event.key == pygame.K_COMMA:
                warp_index = max(warp_index - 1, 0)
            if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                scale /= 1.5
            if event.key == pygame.K_MINUS:
                scale *= 1.5
            if event.key == pygame.K_r:
                state, trail, dv_used, sim_time, crashed = start_state(), [], 0.0, 0.0, False
                prediction = predict(state)

    # ----- 2. Held keys: burns -----
    keys = pygame.key.get_pressed()
    if not crashed and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
        dv = DV_PER_FRAME if keys[pygame.K_UP] else -DV_PER_FRAME
        state = burn(state, dv)
        dv_used += abs(dv)
        prediction = predict(state)
    if not crashed and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        v = state[2:]
        side = np.array([-v[1], v[0]]) / np.linalg.norm(v)    # velocity rotated 90° to the left, length 1
        sign = 1 if keys[pygame.K_LEFT] else -1
        state = np.concatenate([state[:2], v + sign * DV_PER_FRAME * side])
        dv_used += DV_PER_FRAME
        prediction = predict(state)
    # ----- 3. Physics: advance sim time in small steps -----
    if not crashed:
        time_to_simulate = WARPS[warp_index] * real_dt
        n_sub = max(1, int(np.ceil(time_to_simulate / DT)))
        for _ in range(n_sub):
            state = rk4_step(state, time_to_simulate / n_sub)
        sim_time += time_to_simulate
        trail.append(state[:2].copy())
        trail = trail[-600:]                 # keep only the last 600 points
        if np.linalg.norm(state[:2]) < R_EARTH:
            crashed = True

    # ----- 4. Draw -----
    screen.fill((10, 10, 25))
    pygame.draw.circle(screen, (40, 90, 200), to_screen([0, 0], scale), max(2, int(R_EARTH / scale)))
    if len(prediction) > 1:
        pygame.draw.lines(screen, (90, 90, 120), False, [to_screen(p, scale) for p in prediction[:, :2]], 1)
    if len(trail) > 1:
        pygame.draw.lines(screen, (240, 200, 80), False, [to_screen(p, scale) for p in trail], 2)
    pygame.draw.circle(screen, (255, 255, 255), to_screen(state[:2], scale), 4)

    el = orbit_elements(state)
    if 0.001 < el["e"] < 1:                        # skip circles (no direction) and escape orbits (no apoapsis)
        direction = el["e_vec"] / el["e"]          # unit vector pointing at the periapsis
        peri_pos = el["a"] * (1 - el["e"]) * direction
        apo_pos = -el["a"] * (1 + el["e"]) * direction
        p = to_screen(peri_pos, scale)
        a = to_screen(apo_pos, scale)
        pygame.draw.circle(screen, (86, 180, 233), p, 6)          # sky blue, filled = periapsis
        pygame.draw.circle(screen, (230, 159, 0), a, 7, 2)        # orange ring = apoapsis
        screen.blit(font.render("Pe", True, (86, 180, 233)), (p[0] + 8, p[1] - 8))
        screen.blit(font.render("Ap", True, (230, 159, 0)), (a[0] + 8, a[1] - 8))
    alt_km = (np.linalg.norm(state[:2]) - R_EARTH) / 1000
    speed = np.linalg.norm(state[2:])
    lines = [
        f"Time: {sim_time / 3600:6.2f} h     Warp: x{WARPS[warp_index]}",
        f"Altitude: {alt_km:9.0f} km     Speed: {speed:7.0f} m/s",
        f"Periapsis: {el['periapsis_alt_km']:8.0f} km     Apoapsis: {el['apoapsis_alt_km']:8.0f} km",
        f"e = {el['e']:.3f}     Period: {el['period_h']:.2f} h",
        f"Delta-v used: {dv_used:7.0f} m/s",
        "UP/DOWN burn   , . warp   +/- zoom   R reset",
    ]
    if crashed:
        lines.append("CRASHED - press R")
    for i, text in enumerate(lines):
        screen.blit(font.render(text, True, (220, 220, 220)), (10, 10 + 22 * i))

    pygame.display.flip()

pygame.quit()