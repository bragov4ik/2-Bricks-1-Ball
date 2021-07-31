from math import sqrt
from typing import Tuple
import numpy as np

import constants


def distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float]
) -> float:
    return sqrt(
        (point1[0] - point2[0])**2
        + (point1[1] - point2[1])**2)


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
    # As was found in debugging, sometimes computing error cause
    # the algorithm believe that the collision point is located outside
    # the segments (usually at scale of 1e-15).  It seems to happen only
    # on horizontal lines.  Thus, let's add some margin of error.
    minCorner = (
        min(boxCorner1[0], boxCorner2[0]) - constants.ERROR_MARGIN,
        min(boxCorner1[1], boxCorner2[1])
    )
    maxCorner = (
        max(boxCorner1[0], boxCorner2[0]) + constants.ERROR_MARGIN,
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


def mirrorVector2D(
    inputVector: Tuple[float, float],
    mirrorNormal: Tuple[float, float]
) -> Tuple[float, float]:
    vec: np.ndarray = np.array(inputVector)
    normal: np.ndarray = np.array(mirrorNormal)
    # Normalize the normal (lol)
    normal /= np.linalg.norm(normal)
    # Substract 2 projections of movement onto normal to get the
    # reflected vector
    vec -= 2*(normal.dot(vec))*normal
    return (vec[0], vec[1])


def changeOrigin(
    point: Tuple[float, float],
    oldOrigin: Tuple[float, float],
    newOrigin: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Shifts origin of `point`'s coordinates from `oldOrigin` to
    `newOrigin`
    """
    newPoint = []
    for oldCoord, oldOffset, newOffset in zip(point, oldOrigin, newOrigin):
        newPoint.append(oldCoord + oldOffset - newOffset)
    # If the specified origin had less dimensions, leave remaining
    # ones unchanged
    if len(newPoint) < len(point):
        newPoint.extend(point[len(newPoint):])
    return newPoint
