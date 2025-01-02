import pymunk
import math

def smoothing_function(radius: float, distance: float) -> float:
    volume = math.pi * math.pow(radius, 4) / 6
    smoothed = radius - distance
    if distance >= radius: return 0
    return smoothed * smoothed / volume

def smoothing_function_derivative(distance: float, radius: float) -> float:
    if distance >= radius: return 0
    func = distance - radius
    scale = 12 / (math.pi * pow(radius, 4))
    return scale * func

def distance(shape1: pymunk.Circle, shape2: pymunk.Circle) -> float:
    x1, y1 = shape1.body.position
    x2, y2 = shape2.body.position
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def relative_position(shape: pymunk.Circle) -> tuple[float, float]:
    x, y = shape.body.position
    x -= 20
    y -= 20
    return x, y

def angle_ratio(shape1: pymunk.Circle, shape2: pymunk.Circle) -> tuple[float, float]:
    x1, y1 = shape1.body.position
    x2, y2 = shape2.body.position

    if y2 - y1 > 0: x_mult = 1
    else: x_mult = -1

    if x2 - x1 > 0: y_mult = 1
    else: y_mult = -1

    if x1 == x2: return 1 * x_mult, 0
    if y1 == y2: return 0, 1 * y_mult


    slope = abs((y2 - y1) / (x2 - x1))
    total  = slope + 1

    return 1/total * x_mult, slope/total * y_mult

def density_to_pressure(density: float) -> float:
    target_density = 1
    pressure_multiplier = 10000
    dError = density - target_density
    pressure = dError * pressure_multiplier
    return pressure

def shared_pressure(a: float, b: float) -> float:
    a = density_to_pressure(a)
    b = density_to_pressure(b)
    return (a + b) / 2
