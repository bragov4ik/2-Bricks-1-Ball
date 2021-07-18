from math import sqrt
from typing import List, Tuple

import numpy as np

import objects


def lineEqtnFrom2Points(
    lineStart: Tuple[float, float], 
    lineEnd: Tuple[float, float]
    ) -> Tuple[float, float, float]:
    """
    Finds equation of the line (in form Ax + By = C) from 2 given
    points.  If the points coincide, returns an equation of a line
    parallel to y axis.  Result is a tuple (A, B, C)
    """
    (x1, y1) = lineStart
    (x2, y2) = lineEnd
    a, b = 0, 0
    if x1 != x2:
        b = 1
        a = -b*(y1-y2)/(x1-x2)
    elif y1 != y2:
        a = 1
        b = -a*(x1-x2)/(y1-y2)
    else:
        # The points coincide; Let's assume the line is vertical
        a = 1
        b = 0
    c = a*x1 + b*y1
    return (a, b, c)


def pointInBox(
    point: Tuple[float, float],
    boxCorner1: Tuple[float, float],
    boxCorner2: Tuple[float, float]
    ) -> bool:
    minCorner = (
        min(boxCorner1[0], boxCorner2[0]),
        min(boxCorner1[1], boxCorner2[1])
        )
    maxCorner = (
        max(boxCorner1[0], boxCorner2[0]),
        max(boxCorner1[1], boxCorner2[1])
        )
    return (minCorner[0] <= point[0] <= maxCorner[0]
        and minCorner[1] <= point[1] <= maxCorner[1])


def rotationMatrix2D(
    alpha: float
    ) -> np.ndarray:
    """
    Calculates 2D rotational matrix for given angle alpha (counter
    clockwise for xy-plane with inverted y, like in our case)
    """
    cosine = np.math.cos(alpha)
    sine = np.math.sin(alpha)
    return np.array([
        [cosine, -sine],
        [sine, cosine]
    ])


def collisionSegmentCircle(
    segStart: Tuple[float, float], 
    segEnd: Tuple[float, float], 
    circOrig: Tuple[float, float], 
    circR: float
    ) -> List[objects.Collision]:
    """
    Detects if the segment between 2 given points intersects with the 
    circle (defined by origin and radius as tuples).
    @returns List of collisions (0 to 2 points).  Normals of them are
    vectors orthogonal to a surface of the circle
    """
    (x0, y0) = circOrig
    (x1, y1) = segStart
    (x2, y2) = segEnd
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
    # Filter out intersections outside the segment
    resultInSegment = []
    for point in result:
        if pointInBox(point, segStart, segEnd):
            resultInSegment.append(point)

    # Find normals
    collisions = []
    for point in resultInSegment:
        nextCol = objects.Collision()
        nextCol.position = point
        # It lies on the circle, so we can easily find normal vector
        normal = (
            point[0] - circOrig[0],
            point[1] - circOrig[1]
        )
        nextCol.normal = normal
        collisions.append(nextCol)
    return collisions


def collisionSegments(
    seg1Start: Tuple[float, float],
    seg1End: Tuple[float, float],
    seg2Start: Tuple[float, float],
    seg2End: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
    """
    Finds collisions of 2 line segments.  If they are parallel,
    empty list is returned.  In case of (partly) coinciding segments,
    collision point closest to a start of segment 1 is given.
    @returns List of collisions (0 or 1) with normal - any orthogonal 
    vector to segment 2
    """
    # Find the normal right away
    normal: np.ndarray = (
        rotationMatrix2D(np.math.pi/2) 
        @ np.array([seg2End[0]-seg2Start[0], seg2End[1]-seg2Start[1]]))
    # Evaluate formulae for lines for given segments in form of
    # ax + by = c
    coefficients = np.array([
        lineEqtnFrom2Points(seg1Start, seg1End),
        lineEqtnFrom2Points(seg2Start, seg2End)
    ])
    # Az = b; z = (x, y)
    A = np.copy(coefficients[:, :2])
    b = np.copy(coefficients[:, 2:])
    if np.linalg.det(A) != 0:
        # Invertible matrix, the unique solution exists
        solution = (np.linalg.inv(A) @ b).flatten().tolist()
        if (pointInBox(solution, seg1Start, seg1End)
            and pointInBox(solution, seg2Start, seg2End)):
            # The intersection is in the segments
            col = objects.Collision()
            col.position = (solution[0], solution[1])
            col.normal = (normal[0], normal[1])
            return [col]
        else:
            return []

    else:
        # Check if the lines coincide
        if np.linalg.matrix_rank(A) == 0:
            # In theory shouldn't happen at all
            raise ValueError("Zero rank of coefficient matrix")
    
        # Rows are dependant, find their relation
        multiplier = 0
        if A[0][0] == 0:
            multiplier = A[0][1] / A[1][1]
        elif A[0][1] == 0:
            multiplier = A[0][0] / A[1][0]
        else:
            # Also always shouldn't be the case, checking to play
            # it safe
            raise ValueError("First row consists of only zeroes!")
        A[1, :] *= multiplier
        b[1, :] *= multiplier
        # Since rank is 1, we should have 2 equal rows in A
        if abs(b[0][0] - b[1][0]) > 1e-5:   # Accept a little of error
            # They're parallel
            return []
        else:
            # Lines coincide, return solution closest to seg1Start
            pointsOfInterest = [
                seg1Start,
                seg1End,
                seg2Start,
                seg2End
            ]
            closestPoint = None
            minDistance = None
            for point in pointsOfInterest:
                distance = sqrt((point[0] - seg1Start[0])**2
                    + (point[1] - seg1Start[1])**2)
                if (pointInBox(point, seg1Start, seg1End)
                    and pointInBox(point, seg2Start, seg2End)
                    and (minDistance == None 
                    or minDistance > distance)):
                    # The point belongs to both segments and is closer
                    # to seg1Start than previously found one
                    minDistance = distance
                    closestPoint = point
            if closestPoint == None:
                return []
            else:
                col = objects.Collision()
                col.position = (closestPoint[0], closestPoint[1])
                col.normal = (normal[0], normal[1])
                return [col]
            
