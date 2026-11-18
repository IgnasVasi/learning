"""All the boring pygame stuff, written once. Copy-paste this file, never retype it."""
import pygame
from solar import AU

WIDTH, HEIGHT = 1100, 700
CENTRE = (350, 350)
PX_PER_AU = 250

SKY = (86, 180, 233)        # colour-blind-safe palette
ORANGE = (230, 159, 0)
YELLOW = (240, 228, 66)
PURPLE = (204, 121, 167)
GREY = (120, 120, 140)
WHITE = (230, 230, 230)

_screen = None
_font = None


def to_screen(pos):
    """Metres around the Sun -> pixel position."""
    return (int(CENTRE[0] + pos[0] / AU * PX_PER_AU), int(CENTRE[1] - pos[1] / AU * PX_PER_AU))


def sun():
    pygame.draw.circle(_screen, (255, 230, 150), CENTRE, 10)


def orbit_ring(radius_au):
    pygame.draw.circle(_screen, GREY, CENTRE, int(radius_au * PX_PER_AU), 1)


def dot(pos, colour, size=7, label=None):
    """A filled circle at a position in metres, optionally with a label next to it."""
    p = to_screen(pos)
    pygame.draw.circle(_screen, colour, p, size)
    if label:
        _screen.blit(_font.render(label, True, colour), (p[0] + 10, p[1]))


def ring(pos, colour, label=None):
    """An empty circle = 'something WILL be here'."""
    p = to_screen(pos)
    pygame.draw.circle(_screen, colour, p, 9, 2)
    if label:
        _screen.blit(_font.render(label, True, colour), (p[0] + 10, p[1] + 6))


def path(points, colour, width=2):
    """A line through many positions in metres (e.g. a transfer arc)."""
    pygame.draw.lines(_screen, colour, False, [to_screen(p) for p in points], width)


def text(line, words, colour=WHITE):
    """Write on the right-hand panel. line 0 is the top line."""
    _screen.blit(_font.render(words, True, colour), (680, 30 + 26 * line))


def run(update, draw, on_key, title="Simulation"):
    """The game loop. Every frame: keys -> update(dt) -> draw()."""
    global _screen, _font
    pygame.init()
    _screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(title)
    _font = pygame.font.SysFont(None, 26)
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000                          # real seconds since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                on_key(pygame.key.name(event.key))          # "p", "space", ".", "up", ...
        update(dt)
        _screen.fill((10, 10, 25))
        draw()
        pygame.display.flip()
    pygame.quit()