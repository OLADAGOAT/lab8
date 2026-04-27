import random
import pygame
from dataclasses import dataclass
from typing import List, Tuple

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 500
MIN_SQUARE_SIZE = 5
MAX_SQUARE_SIZE = 50
SQUARE_COUNT = 20
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
    pygame.display.set_caption("FLEE AND DIE")
    return screen


def create_one_square() -> Square:
    square_size = random.randint(MIN_SQUARE_SIZE, MAX_SQUARE_SIZE)
    x = random.randint(0, SCREEN_WIDTH - square_size)
    y = random.randint(0, SCREEN_HEIGHT - square_size)

    vx = 5 / square_size
    vy = 5 / square_size

    rect = pygame.Rect(x, y, square_size, square_size)
    life_span = random.uniform(MIN_LIFE_SPAN, MAX_LIFE_SPAN)

    return Square(rect, (vx, vy), life_span)


def create_squares(count: int) -> List[Square]:
    squares: List[Square] = []
    for _ in range(count):
        squares.append(create_one_square())
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
            if i != j and other.rect.width > square.rect.width:
                dx = square.rect.centerx - other.rect.centerx
                dy = square.rect.centery - other.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if 0 < distance < 150:
                    dx /= distance
                    dy /= distance
                    square.velocity = (
                        square.velocity[0] + dx * 2,
                        square.velocity[1] + dy * 2,
                    )

        square.rect.x += int(square.velocity[0])
        square.rect.y += int(square.velocity[1])

        square.rect.x += random.randint(-1, 1)
        square.rect.y += random.randint(-1, 1)

        if square.rect.left < 0 or square.rect.right > SCREEN_WIDTH:
            square.velocity = (-square.velocity[0], square.velocity[1])
            square.rect.x = max(0, min(square.rect.x, SCREEN_WIDTH - square.rect.width))

        if square.rect.top < 0 or square.rect.bottom > SCREEN_HEIGHT:
            square.velocity = (square.velocity[0], -square.velocity[1])
            square.rect.y = max(0, min(square.rect.y, SCREEN_HEIGHT - square.rect.height))

    for i in range(len(squares) - 1, -1, -1):
        if squares[i].age >= squares[i].life_span:
            squares.pop(i)
            squares.append(create_one_square())


def draw_squares(screen: pygame.Surface, squares: List[Square], fps: float) -> None:
    screen.fill((30, 30, 30))

    for square in squares:
        pygame.draw.rect(screen, (255, 255, 255), square.rect)

    font = pygame.font.Font(None, 28)
    fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()

def update_squares(squares: List[Square], dt: float) -> None:
    for i, square in enumerate(squares):
        square.age += dt

        for j, other in enumerate(squares):
            if i != j:
                dx = square.rect.centerx - other.rect.centerx
                dy = square.rect.centery - other.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < 150:
                    if square.rect.width > other.rect.width:
                        square.velocity = (
                            square.velocity[0] - dx,
                            square.velocity[1] - dy,
                        )
                    elif square.rect.width < other.rect.width:
                        square.velocity = (
                            square.velocity[0] + dx,
                            square.velocity[1] + dy,
                        )

        square.rect.x += int(square.velocity[0])
        square.rect.y += int(square.velocity[1])

    for i in range(len(squares) - 1, -1, -1):
        if squares[i].age >= squares[i].life_span:
            squares[i] = create_one_square()


def main() -> None:
    screen = initialize_pygame()
    squares = create_squares(SQUARE_COUNT)
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