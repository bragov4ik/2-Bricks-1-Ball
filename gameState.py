from math import copysign
from typing import List, Type
import utilities
import collisions
import constants
import customObjects


class GameState:
    ball: customObjects.Ball
    playerBrick: customObjects.Player
    enemyBrick: customObjects.Player
    playerPosition = 0
    enemyPosition = 0
    playerScore = 0
    enemyScore = 0
    # Flags used to not check the same collision twice.
    # 4 sides : LEFT, UP, RIGHT, DOWN, player and enemy.  Needs to be
    # preserved between ticks
    collisionsResolved: List[bool]
    history = []
    aboba = 0

    def __init__(self) -> None:
        self.ball = customObjects.Ball(
            x=constants.BALL_STARTING_POS[0],
            y=constants.BALL_STARTING_POS[1],
            scale=constants.BALL_RADIUS
        )
        self.ball.xVel = constants.BALL_STARTING_SPEED[0]
        self.ball.yVel = constants.BALL_STARTING_SPEED[1]
        self.playerBrick = customObjects.Player(
            xScale=constants.PLAYER_SIZE[0],
            yScale=constants.PLAYER_SIZE[1]
        )
        self.enemyBrick = customObjects.Player(
            x=constants.GAME_FIELD_SIZE[0]-constants.PLAYER_SIZE[0],
            xScale=constants.PLAYER_SIZE[0],
            yScale=constants.PLAYER_SIZE[1]
        )
        self.collisionsResolved = [False]*6

    def tickState(self, t):
        # Players' moves
        for player in (self.playerBrick, self.enemyBrick):
            # Convert the problem of moving brick into a ball to
            # moving ball into a brick (we see brick as the point of
            # reference), since we already have such collision checking
            # implemented.

            # The ball therefore moves in opposite direction (as
            # point of reference has changed)
            ballMove = (
                -player.desiredMove[0],
                -player.desiredMove[1]
            )
            ballPos = (self.ball.xPos, self.ball.yPos)

            # Get the collision point
            returnedVal = collisions.getClosestCollision(
                ballPos,
                collisions.collisionBallBrick(
                    self.ball, player, ballPos, ballMove
                )
            )
            if returnedVal == None:
                # No collisions with the ball, can move freely
                player.moveBy(player.desiredMove[0], player.desiredMove[1])
                player.setDesiredMove(0.0, 0.0)
            else:
                # Collision found! Handle:
                (collision, _) = returnedVal

                # Player's move would be the vector starting from the
                # collision point to the ball

                # x component is always static, so let's leave it
                yPlayerMove = ballPos[1] - collision.position[1]
                # To prevent repeated colliding with the ball (since
                # it causes the ball to bounce inside the brick), add
                # a little gap.
                yPlayerMove = (yPlayerMove
                               - copysign(
                                   constants.ERROR_MARGIN,
                                   yPlayerMove
                               ))
                newPlayerMove = (
                    0,
                    yPlayerMove
                )
                player.moveBy(newPlayerMove[0], newPlayerMove[1])
                player.setDesiredMove(0.0, 0.0)

        # Ball physics
        curMove = (
            self.ball.xVel*t*1e-1,
            self.ball.yVel*t*1e-1
        )
        curStart = (
            self.ball.xPos,
            self.ball.yPos
        )
        curEnd = (
            curStart[0] + curMove[0],
            curStart[1] + curMove[1]
        )

        r = self.ball.xScale
        # LEFT, UP, RIGHT, DOWN
        sides = (
            (
                (r, r),
                (r, r+constants.GAME_FIELD_SIZE[1])
            ),
            (
                (r, r),
                (-r+constants.GAME_FIELD_SIZE[0], r)
            ),
            (
                (-r+constants.GAME_FIELD_SIZE[0], r),
                (
                    -r+constants.GAME_FIELD_SIZE[0],
                    -r+constants.GAME_FIELD_SIZE[1]
                )
            ),
            (
                (r, -r+constants.GAME_FIELD_SIZE[1]),
                (
                    -r+constants.GAME_FIELD_SIZE[0],
                    -r+constants.GAME_FIELD_SIZE[1]
                )
            )
        )
        collisionList: List[customObjects.Collision] = None
        # Indexes in collisionsResolved list of found collisions
        collisionsIDs: List[int] = []
        while (
            collisionList == None
            or (collisionList
                and utilities.distance(curStart, curEnd) != 0)    # Not magnitude of move!!!
        ):
            # Find all possible collisions
            collisionList = []
            collisionsIDs = []
            for i in range(len(sides)):
                if self.collisionsResolved[i]:
                    # Resolution of the collision skips only one
                    # iteration
                    self.collisionsResolved[i] = False
                    continue
                side = sides[i]
                newCollisions = collisions.collisionVectorSegment(
                    curStart, curEnd, side[0], side[1]
                )
                collisionList += newCollisions
                if newCollisions:
                    collisionsIDs += [i]*len(newCollisions)
            if self.collisionsResolved[4]:
                self.collisionsResolved[4] = False
            else:
                newCollisions = collisions.collisionBallBrick(
                    self.ball,
                    self.playerBrick,
                    curStart,
                    curMove
                )
                collisionList += newCollisions
                if newCollisions:
                    collisionsIDs += [4]*len(newCollisions)
            if self.collisionsResolved[5]:
                self.collisionsResolved[5] = False
            else:
                newCollisions = collisions.collisionBallBrick(
                    self.ball,
                    self.enemyBrick,
                    curStart,
                    curMove
                )
                collisionList += newCollisions
                if newCollisions:
                    collisionsIDs += [5]*len(newCollisions)
            if len(collisionList) == 0:
                continue

            # Extract the one closest to the start
            closest = collisions.getClosestCollision(
                curStart,
                collisionList
            )
            if closest == None:
                # Must not happen as length check for 0 is not passed
                raise IndexError("No collisions to handle!")
            closestCollision = closest[0]
            closestCollisionID = collisionsIDs[closest[1]]

            # Resolve the closest collision
            curMove = collisions.resolveCollision(
                curStart,
                curMove,
                closestCollision
            )
            curStart = closestCollision.position
            curEnd = (
                curStart[0] + curMove[0],
                curStart[1] + curMove[1]
            )
            (self.ball.xVel, self.ball.yVel) = utilities.mirrorVector2D(
                (self.ball.xVel, self.ball.yVel),
                closestCollision.normal
            )
            self.collisionsResolved[closestCollisionID] = True
        # No more collisions here
        curEnd = (
            curStart[0] + curMove[0],
            curStart[1] + curMove[1]
        )
        self.ball.xPos = curEnd[0]
        self.ball.yPos = curEnd[1]
