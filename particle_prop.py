import pymunk
import math

def smoothing_function(radius: float, distance: float) -> float:
    volume = math.pi * math.pow(radius, 5) /10
    smoothed = max(0.0, radius - distance)
    if smoothed == 0: return 0
    return smoothed * smoothed * smoothed / volume

def distance(shape1: pymunk.Circle, shape2: pymunk.Circle) -> float:
    x1, y1 = shape1.body.position
    x2, y2 = shape2.body.position
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def relative_position(shape: pymunk.Circle) -> tuple:
    x, y = shape.body.position
    x -= 20
    y -= 20
    return x, y