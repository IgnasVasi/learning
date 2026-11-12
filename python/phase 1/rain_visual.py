import pygame
from rain_classes import Raindrop, Person
from rain_sim import add_new_drops, DT, DISTANCE, X_MIN, RAIN_SPEED

WIND_SPEED = -2.0            # [m/s], positive = blowing to the right (from behind)
WALK_SPEED = 2.0            # [m/s]

SCALE = 80                  # pixels per metre
WIDTH, HEIGHT = 1100, 320   # window size [pixels]
GROUND_Y = 280              # pixel row of the ground
STREAK = 0.03               # length of each drop's streak, in seconds of motion


def to_screen(x, y):
    """metres (y up) -> pixels (y down)"""
    return int((x - X_MIN) * SCALE), int(GROUND_Y - y * SCALE)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Walk or run in the rain?")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

person = Person(speed=WALK_SPEED)
drops = []
hits = 0
running = True

while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update
    add_new_drops(drops, WIND_SPEED)
    if person.x < DISTANCE:
        person.step(DT)
    survivors = []
    for drop in drops:
        drop.step(DT, WIND_SPEED)
        if person.is_hit(drop):
            hits += 1
        elif not drop.on_ground():
            survivors.append(drop)
    drops = survivors

    # 3. Draw
    screen.fill((25, 25, 40))
    pygame.draw.line(screen, (90, 160, 90), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
    for drop in drops:
        head = to_screen(drop.x, drop.y)
        tail = to_screen(drop.x - WIND_SPEED * STREAK, drop.y + RAIN_SPEED * STREAK)
        pygame.draw.line(screen, (120, 170, 255), tail, head, 1)
    left, top = to_screen(person.x, person.height)
    pygame.draw.rect(screen, (240, 200, 80),
                     (left, top, int(person.width * SCALE), int(person.height * SCALE)))
    text = font.render(f"Hits: {hits}   Walk: {person.speed} m/s   Wind: {WIND_SPEED} m/s",
                       True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # 4. Show
    pygame.display.flip()
    clock.tick(100)

pygame.quit()