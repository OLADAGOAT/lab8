# FLEEEEEEE - Architecture Diagrams

## Project Overview
**FLEEEEEEE** is a Pygame-based interactive animation application that simulates the behavior of autonomous squares on a 2D canvas. The application demonstrates emergent behavior through simple physics-based rules: larger squares chase smaller ones, smaller squares flee from larger ones.

---

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Pygame Environment"
        PG["pygame<br/>(Graphics & Events)"]
    end
    
    subgraph "Main Application"
        ML["main()"]
        IE["handle_events()"]
        US["update_squares()"]
        DS["draw_squares()"]
        CLK["Clock<br/>(FPS Controller)"]
    end
    
    subgraph "Data Models"
        SQ["Square<br/>• rect<br/>• velocity<br/>• life_span<br/>• age"]
        SQLIST["List[Square]"]
    end
    
    subgraph "Factory Functions"
        COS["create_one_square()"]
        CS["create_squares()"]
    end
    
    subgraph "Initialization"
        IP["initialize_pygame()"]
    end
    
    PG -->|Display| DS
    PG -->|Input| IE
    
    ML -->|Init| IP
    ML -->|Create| CS
    ML -->|Loop| IE
    ML -->|Loop| CLK
    ML -->|Loop| US
    ML -->|Loop| DS
    
    IP -->|Returns| PG
    
    CS -->|Creates| SQLIST
    CS -->|Uses| COS
    COS -->|Returns| SQ
    
    IE -->|Polls| PG
    
    US -->|Updates| SQLIST
    US -->|Physics Logic| SQ
    
    DS -->|Renders| SQ
    DS -->|Displays| PG
    DS -->|Uses| CLK
    
    CLK -->|Throttles| ML
```

**Key Components:**
- **Pygame Environment**: Handles graphics rendering and input events
- **Main Application**: Game loop and core logic functions
- **Data Models**: Square dataclass and list management
- **Factory Functions**: Creation and initialization of Square objects
- **Initialization**: Setup and startup functions

---

## Main Loop Sequence Diagram

```mermaid
sequenceDiagram
    participant Main as main()
    participant Events as handle_events()
    participant Update as update_squares()
    participant Draw as draw_squares()
    participant Pygame as pygame
    
    loop Each Frame
        Main->>Events: Check for QUIT
        Events->>Pygame: Poll events
        Pygame-->>Events: Event queue
        Events-->>Main: Continue? (bool)
        
        Main->>Main: dt = clock.tick(FPS)
        
        Main->>Update: update_squares(squares, dt)
        activate Update
        Update->>Update: For each square: age += dt
        Update->>Update: Check interactions (n²)
        Update->>Update: Apply chase/flee behavior
        Update->>Update: Update position
        Update->>Update: Check collisions
        Update->>Update: Remove dead squares
        Update->>Update: Create replacement squares
        deactivate Update
        Update-->>Main: Return
        
        Main->>Draw: draw_squares(screen, squares, fps)
        activate Draw
        Draw->>Pygame: Clear screen
        Draw->>Pygame: Draw all squares
        Draw->>Draw: Render FPS text
        Draw->>Pygame: Flip display
        deactivate Draw
        Draw-->>Main: Return
    end
```

**Sequence:**
1. **Event Handling**: Check for user input (QUIT event)
2. **Timing**: Throttle to target FPS (50 FPS = ~20ms/frame)
3. **Update**: Apply physics, interactions, and lifecycle management
4. **Render**: Draw all squares and UI elements to screen

---

## Interaction Logic Diagram

```mermaid
graph LR
    subgraph "Square A vs Square B"
        START["Distance < 150px?"]
        DIST_YES["Yes"]
        DIST_NO["No"]
        SIZE_CMP["Compare Sizes"]
        A_LARGER["A > B<br/>(Chase)"]
        B_LARGER["A < B<br/>(Flee)"]
        EQUAL["A == B<br/>(Ignore)"]
        CHASE_ACC["Accelerate Toward B<br/>vx += 0.3 * dx<br/>vy += 0.5 * dy"]
        FLEE_ACC["Accelerate Away<br/>vx -= 0.3 * dx<br/>vy -= 0.5 * dy"]
        NO_CHANGE["No velocity change"]
    end
    
    START -->|Distance ≥ 150px| DIST_NO
    START -->|Distance < 150px| DIST_YES
    DIST_NO --> NO_CHANGE
    DIST_YES --> SIZE_CMP
    SIZE_CMP --> A_LARGER
    SIZE_CMP --> B_LARGER
    SIZE_CMP --> EQUAL
    A_LARGER --> CHASE_ACC
    B_LARGER --> FLEE_ACC
    EQUAL --> NO_CHANGE
```

**Behavior Rules:**
- **Interaction Radius**: 150 pixels
- **Chase (Larger → Smaller)**: Accelerate toward target at (vx: 0.3, vy: 0.5)
- **Flee (Smaller → Larger)**: Accelerate away from threat at (vx: -0.3, vy: -0.5)
- **Equal Size**: No interaction
- **Distance Threshold**: Interactions only occur within 150 pixels

---

## Configuration Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `SCREEN_WIDTH` | 500 | Canvas width in pixels |
| `SCREEN_HEIGHT` | 700 | Canvas height in pixels |
| `MIN_SQUARE_SIZE` | 5 | Minimum square dimension |
| `MAX_SQUARE_SIZE` | 50 | Maximum square dimension |
| `SQUARE_COUNT` | 20 | Initial and maintained population |
| `FPS` | 50 | Target frames per second |
| `MIN_LIFE_SPAN` | 3.0 | Minimum lifespan in seconds |
| `MAX_LIFE_SPAN` | 8.0 | Maximum lifespan in seconds |
| `INTERACTION_RADIUS` | 150 | Distance threshold for behavior |

---

## Data Model: Square Dataclass

```python
@dataclass
class Square:
    rect: pygame.Rect              # Position (x, y) and dimensions (width, height)
    velocity: Tuple[float, float]  # (vx, vy) - movement per frame
    life_span: float               # Maximum age in seconds (3-8)
    age: float = 0.0               # Current age, incremented each frame
```

**Lifecycle:**
- Birth: Random position, size (5-50px), velocity (inverse to size), lifespan (3-8s)
- Growth: Age accumulates each frame
- Death: Removed when `age >= life_span`
- Replacement: New square immediately created

---

## Performance Profile

- **Fixed Population**: Always maintains 20 squares
- **Time Complexity**: O(n²) per frame (20² = 400 pairwise checks)
- **Frame Rate**: 50 FPS target (20ms per frame)
- **Memory**: Minimal (~20 Square objects + Pygame surface)

---

## Design Patterns

1. **Dataclass Pattern**: Structured data container for Square entities
2. **Factory Pattern**: `create_one_square()` and `create_squares()` for object creation
3. **Game Loop Pattern**: Classic event → update → render cycle
4. **Collision Handling**: Physics-based boundary reflection with clamping