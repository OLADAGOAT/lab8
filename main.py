import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 50

MIN_LIFE_SPAN = 3.0
MAX_LIFE_SPAN = 8.0


@dataclass
class Square:
    rect: pygame.Rect
    velocity: Tuple[float, float]
    life_span: float
    age: float = 0.0


def initialize_pygame() -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("FLEEEEEEE")
    return screen


def create_one_square(square_size: int) -> Square:
    x = random.randint(0, SCREEN_WIDTH - square_size)
    y = random.randint(0, SCREEN_HEIGHT - square_size)

    vx = 10 / square_size
    vy = 10 / square_size

    rect = pygame.Rect(x, y, square_size, square_size)
    life_span = random.uniform(MIN_LIFE_SPAN, MAX_LIFE_SPAN)

    return Square(rect, (vx, vy), life_span)


def create_squares() -> List[Square]:
    squares: List[Square] = []

    sizes = [25] * 5 + [10] * 10 + [4] * 30

    for square_size in sizes:
        squares.append(create_one_square(square_size))

    return squares


def handle_events() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False


def update_squares(squares: List[Square], dt: float) -> None:
    for i, square in enumerate(squares):
        square.age += dt

        for j, other in enumerate(squares):
            if i != j:
                dx = other.rect.centerx - square.rect.centerx
                dy = other.rect.centery - square.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if 0 < distance < 150:
                    dx /= distance
                    dy /= distance

                    if square.rect.width > other.rect.width:
                        square.velocity = (
                            square.velocity[0] + dx * 0.3,
                            square.velocity[1] + dy * 0.5,
                        )

                    elif square.rect.width < other.rect.width:
                        square.velocity = (
                            square.velocity[0] - dx * 0.3,
                            square.velocity[1] - dy * 0.5,
                        )

        square.rect.x += int(square.velocity[0])
        square.rect.y += int(square.velocity[1])

        square.rect.x += random.randint(-1, 1)
        square.rect.y += random.randint(-1, 1)

        # Screen wrapping instead of bouncing
        if square.rect.left > SCREEN_WIDTH:
            square.rect.right = 0
        elif square.rect.right < 0:
            square.rect.left = SCREEN_WIDTH

        if square.rect.top > SCREEN_HEIGHT:
            square.rect.bottom = 0
        elif square.rect.bottom < 0:
            square.rect.top = SCREEN_HEIGHT

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