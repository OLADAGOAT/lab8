import math
import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 50

MIN_LIFE_SPAN = 3.0
MAX_LIFE_SPAN = 8.0
MAX_SQUARE_SIZE = 60
GROWTH_SPEED = 500


@dataclass
class Square:
    rect: pygame.Rect
    velocity: Tuple[float, float]
    life_span: float
    age: float = 0.0
    target_size: int = 0
    growth_remaining_ms: int = 0


def initialize_pygame() -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving Squares")
    return screen


def create_one_square(size: int) -> Square:
    x = random.randint(0, SCREEN_WIDTH - size)
    y = random.randint(0, SCREEN_HEIGHT - size)

    speed = 10 / size
    rect = pygame.Rect(x, y, size, size)
    life_span = random.uniform(MIN_LIFE_SPAN, MAX_LIFE_SPAN)

    return Square(rect, (speed, speed), life_span, 0.0, size, 0)


def create_squares() -> List[Square]:
    sizes = [25] * 5 + [10] * 10 + [4] * 30
    squares: List[Square] = []

    for size in sizes:
        squares.append(create_one_square(size))

    return squares


def handle_events() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False


def check_collision(a: Square, b: Square) -> bool:
    return a.rect.colliderect(b.rect)


def start_growth(square: Square, prey_size: int) -> None:
    growth = max(1, prey_size // 4)
    square.target_size = min(square.target_size + growth, MAX_SQUARE_SIZE)
    square.growth_remaining_ms = GROWTH_SPEED


def apply_growth(square: Square, dt: float) -> None:
    if square.growth_remaining_ms <= 0:
        return

    current_size = square.rect.width

    if current_size >= square.target_size:
        square.growth_remaining_ms = 0
        return

    growth_step = max(1, math.ceil((square.target_size - current_size) * dt * 1000 / square.growth_remaining_ms))
    new_size = min(current_size + growth_step, square.target_size)

    center = square.rect.center
    square.rect.width = new_size
    square.rect.height = new_size
    square.rect.center = center

    speed = 10 / new_size
    square.velocity = (speed, speed)

    square.growth_remaining_ms -= int(dt * 1000)

    if square.rect.width >= square.target_size:
        square.growth_remaining_ms = 0


def wrap_square(square: Square) -> None:
    if square.rect.left > SCREEN_WIDTH:
        square.rect.right = 0
    elif square.rect.right < 0:
        square.rect.left = SCREEN_WIDTH

    if square.rect.top > SCREEN_HEIGHT:
        square.rect.bottom = 0
    elif square.rect.bottom < 0:
        square.rect.top = SCREEN_HEIGHT


def move_away_or_toward(square: Square, other: Square) -> None:
    dx = other.rect.centerx - square.rect.centerx
    dy = other.rect.centery - square.rect.centery
    distance = math.hypot(dx, dy)

    if distance == 0 or distance >= 150:
        return

    dx /= distance
    dy /= distance

    vx, vy = square.velocity

    if square.rect.width > other.rect.width:
        vx += dx * 0.3
        vy += dy * 0.5
    elif square.rect.width < other.rect.width:
        vx -= dx * 0.3
        vy -= dy * 0.5

    square.velocity = (vx, vy)


def update_squares(squares: List[Square], dt: float) -> None:
    for i, square in enumerate(squares):
        square.age += dt
        apply_growth(square, dt)

        for j, other in enumerate(squares):
            if i != j:
                move_away_or_toward(square, other)

        square.rect.x += int(square.velocity[0])
        square.rect.y += int(square.velocity[1])

        square.rect.x += random.randint(-1, 1)
        square.rect.y += random.randint(-1, 1)

        wrap_square(square)

    for i in range(len(squares)):
        for j in range(i + 1, len(squares)):
            if check_collision(squares[i], squares[j]):
                if squares[i].rect.width > squares[j].rect.width:
                    prey_size = squares[j].rect.width
                    start_growth(squares[i], prey_size)
                    squares[j] = create_one_square(prey_size)

                elif squares[j].rect.width > squares[i].rect.width:
                    prey_size = squares[i].rect.width
                    start_growth(squares[j], prey_size)
                    squares[i] = create_one_square(prey_size)

    for i in range(len(squares) - 1, -1, -1):
        if squares[i].age >= squares[i].life_span:
            same_size = squares[i].rect.width
            squares.pop(i)
            squares.append(create_one_square(same_size))


def draw_squares(screen: pygame.Surface, squares: List[Square], fps: float) -> None:
    screen.fill((30, 30, 30))

    for square in squares:
        pygame.draw.rect(screen, (255, 255, 255), square.rect)

    font = pygame.font.Font(None, 28)
    fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()


def main() -> None:
    screen = initialize_pygame()
    squares = create_squares()
    clock = pygame.time.Clock()

    running = True
    while running:
        if handle_events():
            running = False
            continue

        dt = clock.tick(FPS) / 1000.0
        update_squares(squares, dt)
        draw_squares(screen, squares, clock.get_fps())

    pygame.quit()


if __name__ == "__main__":
    main()