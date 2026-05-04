## Exercise 7

The visual artifact is that trails can draw long strange lines when a square wraps from one side of the screen to the other.

This happens because the old trail point is on one side of the screen and the new point is on the opposite side, so pygame draws a line across the whole screen between those two points.

A possible fix is to clear the trail when a square wraps around the screen, or to avoid drawing a line when the distance between two consecutive trail points is too large.

## Exercise 8


Assumption:
I test the movement speed of one square over time, using its velocity vector as the expected speed.

What I measure:
I compare:
- the expected speed from the velocity vector using math.hypot(vx, vy)
- the measured speed from the difference between two consecutive recorded positions

What I evaluate:
If the measured movement per frame is close to the expected movement per frame, then the square is moving at the correct speed.

Limits of this test:
This is only an approximate test because:
- positions are converted to integers
- random jitter is added to movement
- chase/flee behavior can change the velocity during the simulation
- screen wrapping can create sudden jumps

How it could be improved:
A more reliable test would disable random movement, disable interactions with other squares, and test one square moving alone in a straight line.

## Exercise 15

To validate that boids are flocking, I would measure three things linked to S.A.C.:
Separation, Alignment, and Cohesion.

### What I would measure

1. Separation
I would measure the average distance between each boid and its nearby neighbors.
If boids are too close for too long, separation is not working.
A good result would be that boids avoid overlapping and keep some minimum distance.

2. Alignment
I would measure how similar the velocity directions of nearby boids are.
For example, I could compare the angle of one boid's velocity to the average angle of nearby boids.
If alignment works, nearby boids should move in roughly the same direction.

3. Cohesion
I would measure how far each boid is from the average center of nearby boids.
If cohesion works, boids should not stay too isolated and should tend to move toward the group.

### What I would test

I would run the simulation for a fixed amount of time and compute:
- average nearest-neighbor distance
- average difference in movement direction between neighbors
- average distance to local group center

If flocking is working:
- boids should not collide too much
- boids should have similar headings
- boids should stay grouped instead of dispersing randomly

### How I would implement it

I would create a test mode with global variables.
During the test, I would collect boid positions and velocities over many frames.
Then I would calculate summary values for separation, alignment, and cohesion.

A simple success rule could be:
- average neighbor distance stays above a minimum threshold
- average heading difference stays below a maximum threshold
- average distance to local group center stays below a maximum threshold

### Limits

This test would not prove perfect flocking, but it would give measurable evidence that the three S.A.C. behaviors are happening together.

## Exercise 16

I implemented a simple S.A.C. test in code.

The test runs the simulation with separation, alignment, and cohesion enabled.
After a fixed number of frames, it measures:
- average neighbor distance
- average heading difference
- average distance to local group center

The test returns PASS if:
- boids are not too close
- boids have similar headings
- boids stay reasonably grouped

this is still a simplified test but it gives enough evidence that flocking is happening