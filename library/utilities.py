from math import sqrt
from typing import Tuple
import numpy as np

import library.constants


def distance(
    point_1: Tuple[float, float],
    point_2: Tuple[float, float]
) -> float:
    return sqrt(
        (point_1[0] - point_2[0])**2
        + (point_1[1] - point_2[1])**2)


def line_eqtn_from_2_points(
    line_start: Tuple[float, float],
    line_end: Tuple[float, float]
) -> Tuple[float, float, float]:
    """
    Finds equation of the line (in form Ax + By = C) from 2 given
    points.  If the points coincide, returns an equation of a line
    parallel to y axis.  Result is a tuple (A, B, C)
    """
    (x1, y1) = line_start
    (x2, y2) = line_end
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


def point_in_box(
    point: Tuple[float, float],
    box_corner_1: Tuple[float, float],
    box_corner_2: Tuple[float, float]
) -> bool:
    # As was found in debugging, sometimes computing error cause
    # the algorithm believe that the collision point is located outside
    # the segments (usually at scale of 1e-15).  It seems to happen only
    # on horizontal lines.  Thus, let's add some margin of error.
    min_corner = (
        min(box_corner_1[0], box_corner_2[0]) - library.constants.ERROR_MARGIN,
        min(box_corner_1[1], box_corner_2[1])
    )
    max_corner = (
        max(box_corner_1[0], box_corner_2[0]) + library.constants.ERROR_MARGIN,
        max(box_corner_1[1], box_corner_2[1])
    )

    return (min_corner[0] <= point[0] <= max_corner[0]
            and min_corner[1] <= point[1] <= max_corner[1])


def rotation_matrix_2d(
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


def mirror_vector_2d(
    input_vector: Tuple[float, float],
    mirror_normal: Tuple[float, float]
) -> Tuple[float, float]:
    vec: np.ndarray = np.array(input_vector)
    normal: np.ndarray = np.array(mirror_normal)
    # Normalize the normal (lol)
    normal /= np.linalg.norm(normal)
    # Substract 2 projections of movement onto normal to get the
    # reflected vector
    vec -= 2*(normal.dot(vec))*normal
    return (vec[0], vec[1])


def change_origin(
    point: Tuple[float, float],
    old_origin: Tuple[float, float],
    new_origin: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Shifts origin of `point`'s coordinates from `oldOrigin` to
    `newOrigin`
    """
    new_point = []
    for old_coord, old_offset, new_offset in zip(point, old_origin, new_origin):
        new_point.append(old_coord + old_offset - new_offset)
    # If the specified origin had less dimensions, leave remaining
    # ones unchanged
    if len(new_point) < len(point):
        new_point.extend(point[len(new_point):])
    return new_point
