from math import sqrt
from typing import List, Tuple

# Detects if the line defined by 2 points intersects with the circle
# (defined by origin and radius as tuples)
# @returns List of points of intersections (0 to 2 points)
def collisionLineCircle(
    lineP1: Tuple[float, float], 
    lineP2: Tuple[float, float], 
    circOrig: Tuple[float, float], 
    circR: float
    ) -> List[Tuple[float, float]]:
    (x0, y0) = circOrig
    (x1, y1) = lineP1
    (x2, y2) = lineP2
    result = []
    if x1 != x2:
        # Obtain line equation coefficients
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a*x1

        # Solve quadratic equation for x yielded by substitution
        # of the line equation to the circle equation
        a_quad = a**2 + 1
        b_quad = 2*a*b - 2*a*y0 - 2*x0
        c_quad = x0**2 + (b - y0)**2 - circR**2
        det = b_quad**2 - 4*a_quad*c_quad

        x_list = []
        if det > 0:
            x_list = [
                (-b_quad + sqrt(det)) / (2*a_quad),
                (-b_quad - sqrt(det)) / (2*a_quad),
            ]
        elif det == 0:
            x_list = [
                -b_quad / (2*a_quad)
            ]
        # Add points of intersection to the result
        for x in x_list:
            result.append((x, a*x + b))
    else:
        # Formula is $y = y_0 + \sqrt{R^2 - (b - x_0)^2}$
        # Since x1 == x2, it doesn't matter which one to use
        b = x1
        temp = circR**2 - (b - x0)**2
        y_list = []
        if temp > 0:
            y_list = [
                y0 + sqrt(temp),
                y0 - sqrt(temp),
            ]
        elif temp == 0:
            y_list = [
                y0
            ]
            
        for y in y_list:
            result.append((x1, y))
    return result
    