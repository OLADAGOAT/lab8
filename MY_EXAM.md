## Exercise 7

The visual artifact is that trails can draw long strange lines when a square wraps from one side of the screen to the other.

This happens because the old trail point is on one side of the screen and the new point is on the opposite side, so pygame draws a line across the whole screen between those two points.

A possible fix is to clear the trail when a square wraps around the screen, or to avoid drawing a line when the distance between two consecutive trail points is too large.