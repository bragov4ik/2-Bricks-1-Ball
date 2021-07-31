from typing import List, NamedTuple, Tuple, Type
from math import sqrt
import numpy as np

import customObjects
import utilities
import constants


def collisionVectorCircle(
    vecStart: Tuple[float, float],
    vecEnd: Tuple[float, float],
    circOrig: Tuple[float, float],
    circR: float
) -> List[customObjects.Collision]:
    """
    Detects if the vector between 2 given points intersects with the 
    circle (defined by origin and radius as tuples).
    @returns List of collisions (0 to 2 points).  Normals of them are
    vectors orthogonal to a surface of the circle
    """
    (x0, y0) = circOrig
    (x1, y1) = vecStart
    (x2, y2) = vecEnd
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
        if utilities.pointInBox(point, vecStart, vecEnd):
            resultInSegment.append(point)

    # Find normals
    collisions = []
    for point in resultInSegment:
        nextCol = customObjects.Collision()
        nextCol.position = point
        # It lies on the circle, so we can easily find normal vector
        normal = (
            point[0] - circOrig[0],
            point[1] - circOrig[1]
        )
        nextCol.normal = normal
        collisions.append(nextCol)
    return collisions


def collisionVectorSegment(
    vecStart: Tuple[float, float],
    vecEnd: Tuple[float, float],
    segStart: Tuple[float, float],
    segEnd: Tuple[float, float]
) -> List[customObjects.Collision]:
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
        utilities.rotationMatrix2D(np.math.pi/2)
        @ np.array([segEnd[0]-segStart[0], segEnd[1]-segStart[1]]))
    # Evaluate formulae for lines for segment and vector in form of
    # ax + by = c
    coefficients = np.array([
        utilities.lineEqtnFrom2Points(vecStart, vecEnd),
        utilities.lineEqtnFrom2Points(segStart, segEnd)
    ])
    # Az = b; z = (x, y)
    A = np.copy(coefficients[:, :2])
    b = np.copy(coefficients[:, 2:])
    if np.linalg.det(A) != 0:
        # Invertible matrix, the unique solution exists
        solution = (np.linalg.inv(A) @ b).flatten().tolist()
        if (utilities.pointInBox(solution, vecStart, vecEnd)
                and utilities.pointInBox(solution, segStart, segEnd)):
            # The intersection is in the segment and the vector
            col = customObjects.Collision()
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
            pointsOfInterest = [
                vecStart,
                vecEnd,
                segStart,
                segEnd
            ]
            closestPoint = None
            minDistance = None
            for point in pointsOfInterest:
                distance = utilities.distance(point, vecStart)
                if (utilities.pointInBox(point, vecStart, vecEnd)
                    and utilities.pointInBox(point, segStart, segEnd)
                    and (minDistance == None
                         or minDistance > distance)):
                    # The point belongs to both segment and vector and
                    # is closer to vecStart than previously found one
                    minDistance = distance
                    closestPoint = point
            if closestPoint == None:
                return []
            else:
                col = customObjects.Collision()
                col.position = (closestPoint[0], closestPoint[1])
                col.normal = (normal[0], normal[1])
                return [col]


class Stadium(NamedTuple):
    """Represents a stadium - a rectangle with rounded corners"""
    # Sides
    leftSide: Tuple[
        Tuple[float, float],    # Start
        Tuple[float, float]     # End
    ]
    rightSide: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    topSide: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    bottomSide: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    # Corners' circles
    leftTopCorner: Tuple[
        Tuple[float, float],    # Center
        float                   # Radius
    ]
    rightTopCorner: Tuple[
        Tuple[float, float],
        float
    ]
    rightBottomCorner: Tuple[
        Tuple[float, float],
        float
    ]
    leftBottomCorner: Tuple[
        Tuple[float, float],
        float
    ]
    # Corners' circles' boxes containing a quarter of the circumference
    # that is the corner
    leftTopCornerBox: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    rightTopCornerBox: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    rightBottomCornerBox: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]
    leftBottomCornerBox: Tuple[
        Tuple[float, float],
        Tuple[float, float]
    ]


def brickBallToStadium(
    ball: customObjects.Ball,
    brick: Type[customObjects.Brick]
) -> Stadium:
    """
    Converts the brick (rectangle) into a stadium (rectangle with
    rounded corners) with radius of the ball (and also thicker than
    the brick by the radius)
    """
    r = ball.xScale
    return Stadium(
        leftSide=(
            (brick.xPos - r, brick.yPos),
            (brick.xPos - r, brick.yPos + brick.yScale)
        ),
        rightSide=(
            (brick.xPos + brick.xScale + r, brick.yPos),
            (brick.xPos + brick.xScale + r, brick.yPos + brick.yScale)
        ),
        topSide=(
            (brick.xPos, brick.yPos - r),
            (brick.xPos + brick.xScale, brick.yPos - r)
        ),
        bottomSide=(
            (brick.xPos, brick.yPos + brick.yScale + r),
            (brick.xPos + brick.xScale, brick.yPos + brick.yScale + r)
        ),
        leftTopCorner=(
            (brick.xPos, brick.yPos),
            r
        ),
        rightTopCorner=(
            (brick.xPos + brick.xScale, brick.yPos),
            r
        ),
        rightBottomCorner=(
            (brick.xPos + brick.xScale, brick.yPos + brick.yScale),
            r
        ),
        leftBottomCorner=(
            (brick.xPos, brick.yPos + brick.yScale),
            r
        ),
        leftTopCornerBox=(
            (brick.xPos, brick.yPos),
            (brick.xPos - r, brick.yPos - r)
        ),
        rightTopCornerBox=(
            (brick.xPos + brick.xScale, brick.yPos),
            (brick.xPos + brick.xScale + r, brick.yPos - r)
        ),
        rightBottomCornerBox=(
            (brick.xPos + brick.xScale, brick.yPos + brick.yScale),
            (brick.xPos + brick.xScale + r, brick.yPos + brick.yScale + r)
        ),
        leftBottomCornerBox=(
            (brick.xPos, brick.yPos + brick.yScale),
            (brick.xPos - r, brick.yPos + brick.yScale + r)
        ),
    )


def collisionBallBrick(
    ball: customObjects.Ball,
    brick: Type[customObjects.Brick],
    movementStart: Tuple[float, float],
    movementVec: Tuple[float, float]
) -> List[customObjects.Collision]:
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
    stadium = brickBallToStadium(ball, brick)
    sSides = [
        stadium.leftSide,
        stadium.rightSide,
        stadium.topSide,
        stadium.bottomSide
    ]
    sCorners = [
        stadium.leftTopCorner,
        stadium.rightTopCorner,
        stadium.leftBottomCorner,
        stadium.rightBottomCorner
    ]
    sCornerBoxes = [
        stadium.leftTopCornerBox,
        stadium.rightTopCornerBox,
        stadium.leftBottomCornerBox,
        stadium.rightBottomCornerBox
    ]

    movementEnd = (
        movementStart[0] + movementVec[0],
        movementStart[1] + movementVec[1]
    )
    collisions: List[customObjects.Collision] = []
    # Check collisions with sides
    for side in sSides:
        collisions += collisionVectorSegment(
            movementStart,
            movementEnd,
            side[0],
            side[1]
        )
    # Collisions with corners
    for (corner, box) in zip(sCorners, sCornerBoxes):
        newCollisions = collisionVectorCircle(
            movementStart,
            movementEnd,
            corner[0],
            corner[1]
        )
        for nextCollision in newCollisions:
            if utilities.pointInBox(nextCollision.position, box[0], box[1]):
                collisions.append(nextCollision)

    return collisions


def resolveCollision(
    startPos: Tuple[float, float],
    moveVec: Tuple[float, float],
    collision: customObjects.Collision
) -> Tuple[float, float]:
    """
    Calculates remaining move vector given the move and collision.  
    Note that collision must lie within the given movement.
    @returns New move vector (to be applied from collision position)
    """
    moveNP: np.ndarray = np.array(moveVec)
    moveToCollisionNP: np.ndarray = np.array(
        collision.position) - np.array(startPos)
    remainingMoveNP: np.ndarray = moveNP - moveToCollisionNP
    remainingMoveNP = np.array(
        utilities.mirrorVector2D(
            remainingMoveNP,
            collision.normal
        )
    )
    return remainingMoveNP


def getClosestCollision(
    point: Tuple[float, float],
    collisions: List[customObjects.Collision]
) -> Tuple[customObjects.Collision, int]:
    """
    Returns closest collision from the provided list to the given point,
    as well as its index in the list.  If empty list is recieved, None
    is returned
    """
    collisionsDist = [
        utilities.distance(point, col.position) for col in collisions
    ]
    if len(collisions) > 0:
        closestCollision = collisions[0]
        closestCollisionIndex = 0
        minDist = collisionsDist[0]
        for i in range(1, len(collisions)):
            if collisionsDist[i] < minDist:
                closestCollision = collisions[i]
                closestCollisionIndex = i
                minDist = collisionsDist[i]
        return (closestCollision, closestCollisionIndex)
    else:
        return None
