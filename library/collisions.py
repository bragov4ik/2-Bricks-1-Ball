from typing import List, NamedTuple, Tuple, Type
from math import sqrt
import numpy as np

import library.customObjects
import library.utilities
import library.constants


def collision_vector_circle(
    vec_start: Tuple[float, float],
    vec_end: Tuple[float, float],
    circ_orig: Tuple[float, float],
    circ_r: float
) -> List[library.customObjects.Collision]:
    """
    Detects if the vector between 2 given points intersects with the 
    circle (defined by origin and radius as tuples).
    @returns List of collisions (0 to 2 points).  Normals of them are
    vectors orthogonal to a surface of the circle
    """
    (x0, y0) = circ_orig
    (x1, y1) = vec_start
    (x2, y2) = vec_end
    result = []
    if x1 != x2:
        # Obtain line equation coefficients
        a = (y2 - y1)/(x2 - x1)
        b = y1 - a*x1

        # Solve quadratic equation for x yielded by substitution
        # of the line equation to the circle equation
        a_quad = a**2 + 1
        b_quad = 2*a*b - 2*a*y0 - 2*x0
        c_quad = x0**2 + (b - y0)**2 - circ_r**2
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
        temp = circ_r**2 - (b - x0)**2
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
    result_in_segment = []
    for point in result:
        if library.utilities.point_in_box(point, vec_start, vec_end):
            result_in_segment.append(point)

    # Find normals
    collisions = []
    for point in result_in_segment:
        next_col = library.customObjects.Collision()
        next_col.position = point
        # It lies on the circle, so we can easily find normal vector
        normal = (
            point[0] - circ_orig[0],
            point[1] - circ_orig[1]
        )
        next_col.normal = normal
        collisions.append(next_col)
    return collisions


def collision_vector_segment(
    vec_start: Tuple[float, float],
    vec_end: Tuple[float, float],
    seg_start: Tuple[float, float],
    seg_end: Tuple[float, float]
) -> List[library.customObjects.Collision]:
    """
    Finds collision of a vector into a segment, if any.  If they are
    parallel, empty list is returned.  In case of (partly) coinciding
    segments, collision point closest to a start of segment 1 is given.
    @returns List of collisions (0 or 1) with normal - any orthogonal 
    vector to segment 2
    """
    # Find the normal right away
    # Doesn't matter which side of the segment the normal should face
    normal: np.ndarray = (
        library.utilities.rotation_matrix_2d(np.math.pi/2)
        @ np.array([seg_end[0]-seg_start[0], seg_end[1]-seg_start[1]]))
    # Evaluate formulae for lines for segment and vector in form of
    # ax + by = c
    coefficients = np.array([
        library.utilities.line_eqtn_from_2_points(vec_start, vec_end),
        library.utilities.line_eqtn_from_2_points(seg_start, seg_end)
    ])
    # Az = b; z = (x, y)
    A = np.copy(coefficients[:, :2])
    b = np.copy(coefficients[:, 2:])
    if np.linalg.det(A) != 0:
        # Invertible matrix, the unique solution exists
        solution = (np.linalg.inv(A) @ b).flatten().tolist()
        if (library.utilities.point_in_box(solution, vec_start, vec_end)
                and library.utilities.point_in_box(solution, seg_start, seg_end)):
            # The intersection is in the segment and the vector
            col = library.customObjects.Collision()
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
            # Lines coincide, return solution closest to vecStart
            points_of_interest = [
                vec_start,
                vec_end,
                seg_start,
                seg_end
            ]
            closest_point = None
            min_distance = None
            for point in points_of_interest:
                distance = library.utilities.distance(point, vec_start)
                if (library.utilities.point_in_box(point, vec_start, vec_end)
                    and library.utilities.point_in_box(point, seg_start, seg_end)
                    and (min_distance == None
                         or min_distance > distance)):
                    # The point belongs to both segment and vector and
                    # is closer to vecStart than previously found one
                    min_distance = distance
                    closest_point = point
            if closest_point == None:
                return []
            else:
                col = library.customObjects.Collision()
                col.position = (closest_point[0], closest_point[1])
                col.normal = (normal[0], normal[1])
                return [col]


class Stadium(NamedTuple):
    """Represents a stadium - a rectangle with rounded corners"""
    # Sides
    left_side: Tuple[
        Tuple[float, float],    # Start
        Tuple[float, float]     # End
    ]
    right_side: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    top_side: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    bottom_side: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    # Corners' circles
    left_top_corner: Tuple[
        Tuple[float, float],    # Center
        float                   # Radius
    ]
    right_top_corner: Tuple[
        Tuple[float, float],
        float
    ]
    right_bottom_corner: Tuple[
        Tuple[float, float],
        float
    ]
    left_bottom_corner: Tuple[
        Tuple[float, float],
        float
    ]
    # Corners' circles' boxes containing a quarter of the circumference
    # that is the corner
    left_top_corner_box: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    right_top_corner_box: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    right_bottom_corner_box: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    left_bottom_corner_box: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]


def brick_ball_to_stadium(
    ball: library.customObjects.Ball,
    brick: Type[library.customObjects.Brick]
) -> Stadium:
    """
    Converts the brick (rectangle) into a stadium (rectangle with
    rounded corners) with radius of the ball (and also thicker than
    the brick by the radius)
    """
    r = ball.x_scale
    return Stadium(
        left_side=(
            (brick.x_pos - r, brick.y_pos),
            (brick.x_pos - r, brick.y_pos + brick.y_scale)
        ),
        right_side=(
            (brick.x_pos + brick.x_scale + r, brick.y_pos),
            (brick.x_pos + brick.x_scale + r, brick.y_pos + brick.y_scale)
        ),
        top_side=(
            (brick.x_pos, brick.y_pos - r),
            (brick.x_pos + brick.x_scale, brick.y_pos - r)
        ),
        bottom_side=(
            (brick.x_pos, brick.y_pos + brick.y_scale + r),
            (brick.x_pos + brick.x_scale, brick.y_pos + brick.y_scale + r)
        ),
        left_top_corner=(
            (brick.x_pos, brick.y_pos),
            r
        ),
        right_top_corner=(
            (brick.x_pos + brick.x_scale, brick.y_pos),
            r
        ),
        right_bottom_corner=(
            (brick.x_pos + brick.x_scale, brick.y_pos + brick.y_scale),
            r
        ),
        left_bottom_corner=(
            (brick.x_pos, brick.y_pos + brick.y_scale),
            r
        ),
        left_top_corner_box=(
            (brick.x_pos, brick.y_pos),
            (brick.x_pos - r, brick.y_pos - r)
        ),
        right_top_corner_box=(
            (brick.x_pos + brick.x_scale, brick.y_pos),
            (brick.x_pos + brick.x_scale + r, brick.y_pos - r)
        ),
        right_bottom_corner_box=(
            (brick.x_pos + brick.x_scale, brick.y_pos + brick.y_scale),
            (brick.x_pos + brick.x_scale + r, brick.y_pos + brick.y_scale + r)
        ),
        left_bottom_corner_box=(
            (brick.x_pos, brick.y_pos + brick.y_scale),
            (brick.x_pos - r, brick.y_pos + brick.y_scale + r)
        ),
    )


def collision_ball_brick(
    ball: library.customObjects.Ball,
    brick: Type[library.customObjects.Brick],
    movement_start: Tuple[float, float],
    movement_vec: Tuple[float, float]
) -> List[library.customObjects.Collision]:
    """
    Finds collision(-s) of the ball moving into the brick.
    @returns List with collision object(-s) if they collide, empty
    list otherwise
    """
    # Collision of ball and brick problem is the same as collision of
    # a point into a brick with rounded corners (=stadium) (with radius
    # being the same as of the ball), such that the stadium is thicker
    # than brick by the radius of the ball
    #
    # With this knowledge, let's find the stadium's properties
    stadium = brick_ball_to_stadium(ball, brick)
    s_sides = [
        stadium.left_side,
        stadium.right_side,
        stadium.top_side,
        stadium.bottom_side
    ]
    s_corners = [
        stadium.left_top_corner,
        stadium.right_top_corner,
        stadium.left_bottom_corner,
        stadium.right_bottom_corner
    ]
    s_corner_boxes = [
        stadium.left_top_corner_box,
        stadium.right_top_corner_box,
        stadium.left_bottom_corner_box,
        stadium.right_bottom_corner_box
    ]

    movement_end = (
        movement_start[0] + movement_vec[0],
        movement_start[1] + movement_vec[1]
    )
    collisions: List[library.customObjects.Collision] = []
    # Check collisions with sides
    for side in s_sides:
        collisions += collision_vector_segment(
            movement_start,
            movement_end,
            side[0],
            side[1]
        )
    # Collisions with corners
    for (corner, box) in zip(s_corners, s_corner_boxes):
        new_collisions = collision_vector_circle(
            movement_start,
            movement_end,
            corner[0],
            corner[1]
        )
        for next_collision in new_collisions:
            if library.utilities.point_in_box(next_collision.position, box[0], box[1]):
                collisions.append(next_collision)

    return collisions


def resolve_collision(
    start_pos: Tuple[float, float],
    move_vec: Tuple[float, float],
    collision: library.customObjects.Collision
) -> Tuple[float, float]:
    """
    Calculates remaining move vector given the move and collision.  
    Note that collision must lie within the given movement.
    @returns New move vector (to be applied from collision position)
    """
    move_np: np.ndarray = np.array(move_vec)
    move_to_collision_np: np.ndarray = np.array(
        collision.position) - np.array(start_pos)
    remaining_move_np: np.ndarray = move_np - move_to_collision_np
    remaining_move_np = np.array(
        library.utilities.mirror_vector_2d(
            remaining_move_np,
            collision.normal
        )
    )
    return remaining_move_np


def get_closest_collision(
    point: Tuple[float, float],
    collisions: List[library.customObjects.Collision]
) -> Tuple[library.customObjects.Collision, int]:
    """
    Returns closest collision from the provided list to the given point,
    as well as its index in the list.  If empty list is recieved, None
    is returned
    """
    collisions_dist = [
        library.utilities.distance(point, col.position) for col in collisions
    ]
    if len(collisions) > 0:
        closest_collision = collisions[0]
        closest_collision_index = 0
        minDist = collisions_dist[0]
        for i in range(1, len(collisions)):
            if collisions_dist[i] < minDist:
                closest_collision = collisions[i]
                closest_collision_index = i
                minDist = collisions_dist[i]
        return (closest_collision, closest_collision_index)
    else:
        return None
