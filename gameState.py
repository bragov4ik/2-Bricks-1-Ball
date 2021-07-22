from typing import List
from utilities import (
    collisionBallBrick,
    collisionVectorSegment,
    distance,
    mirrorVector2D,
    resolveCollision
)
import constants
import objects


class GameState:
    ball: objects.Ball
    playerBrick: objects.Brick
    enemyBrick: objects.Brick
    playerPosition = 0
    enemyPosition = 0
    playerScore = 0
    enemyScore = 0
    # Flags used to not check the same collision twice
    # 4 sides (order is the same as in sides), player and enemy.  Needs
    # to be preserved between ticks
    collisionsResolved: List[bool]

    def __init__(self) -> None:
        self.ball = objects.Ball(
            x=constants.BALL_STARTING_POS[0],
            y=constants.BALL_STARTING_POS[1]
        )
        self.ball.xVel = constants.BALL_STARTING_SPEED[0]
        self.ball.yVel = constants.BALL_STARTING_SPEED[1]
        self.playerBrick = objects.Brick()
        self.enemyBrick = objects.Brick(
            x=constants.GAME_FIELD_SIZE[0]-constants.PLAYER_SIZE[0]
        )
        self.collisionsResolved = [False]*6

    def tickState(self, t):
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
                (r, -r+constants.GAME_FIELD_SIZE[1]),
                (
                    -r+constants.GAME_FIELD_SIZE[0],
                    -r+constants.GAME_FIELD_SIZE[1]
                )
            ),
            (
                (-r+constants.GAME_FIELD_SIZE[0], r),
                (
                    -r+constants.GAME_FIELD_SIZE[0],
                    -r+constants.GAME_FIELD_SIZE[1]
                )
            )
        )
        collisions: List[objects.Collision] = None
        # Indexes in collisionsResolved list of found collisions
        collisionsIDs: List[int] = []
        while (
            collisions == None
            or (collisions
                and distance(curStart, curEnd) != 0)    # Not magnitude of move!!!
        ):
            # Find all possible collisions
            collisions = []
            collisionsIDs = []
            for i in range(len(sides)):
                if self.collisionsResolved[i]:
                    # Resolution of the collision skips only one
                    # iteration
                    self.collisionsResolved[i] = False
                    continue
                side = sides[i]
                newCollisions = collisionVectorSegment(
                    curStart, curEnd, side[0], side[1]
                )
                collisions += newCollisions
                if newCollisions:
                    collisionsIDs += [i]*len(newCollisions)
            if self.collisionsResolved[4]:
                self.collisionsResolved[4] = False
            else:
                newCollisions = collisionBallBrick(
                    self.ball,
                    self.playerBrick,
                    curStart,
                    curMove
                )
                collisions += newCollisions
                if newCollisions:
                    collisionsIDs += [4]*len(newCollisions)
            if self.collisionsResolved[5]:
                self.collisionsResolved[5] = False
            else:
                newCollisions = collisionBallBrick(
                    self.ball,
                    self.enemyBrick,
                    curStart,
                    curMove
                )
                collisions += newCollisions
                if newCollisions:
                    collisionsIDs += [5]*len(newCollisions)
            if len(collisions) == 0:
                continue
            # Extract the one closest to the start (that does not
            # coincide with it to avoid handling one collision twice)
            collisionsDist = [
                distance(curStart, col.position) for col in collisions
            ]
            # It is guaranteed that first entry exists as length check
            # for 0 is not passed
            closestCollision = collisions[0]
            closestCollisionID = collisionsIDs[0]
            minDist = collisionsDist[0]
            for i in range(1, len(collisions)):
                if collisionsDist[i] < minDist:
                    closestCollision = collisions[i]
                    closestCollisionID = collisionsIDs[i]
                    minDist = collisionsDist[i]

            # Resolve the closest collision
            print("Handled collision!")
            curMove = resolveCollision(
                curStart,
                curMove,
                closestCollision
            )
            curStart = closestCollision.position
            curEnd = (
                curStart[0] + curMove[0],
                curStart[1] + curMove[1]
            )
            (self.ball.xVel, self.ball.yVel) = mirrorVector2D(
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
