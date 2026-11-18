from engine import run, sun, orbit_ring, dot, text, SKY, ORANGE
from solar import earth, venus, phase_deg

WARPS = [2, 10, 30, 60]         # days per real second
now = 0.0                       # today's date, in days
warp = 2                        # index into WARPS


def on_key(key):
    global warp
    if key == ".":
        warp = min(warp + 1, len(WARPS) - 1)
    if key == ",":
        warp = max(warp - 1, 0)

def update(dt):
    global now
    now = now + WARPS[warp] * dt


def draw():
    sun()
    orbit_ring(1.0)
    orbit_ring(0.723)
    dot(earth(now)[0], SKY, label="Earth")
    dot(venus(now)[0], ORANGE, label="Venus")
    text(0, f"Day {now:.0f}     speed {WARPS[warp]} days/s")
    text(1, f"Venus angle: {phase_deg(now):+.0f} deg   (window at -54)")                # blank 2: "Venus angle: ..." using phase_deg(now)


run(update, draw, on_key, "My mission")