from typing import List
from utilities import (
    collisionBallBrick,
    collisionVectorSegment,
    distance,
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


    def __init__(self) -> None:
        self.ball = objects.Ball(
            x=constants.GAME_FIELD_SIZE[0]/2, 
            y=constants.GAME_FIELD_SIZE[1]/2
        )
        self.ball.xVel = 1
        self.ball.yVel = 1
        self.playerBrick = objects.Brick()
        self.enemyBrick = objects.Brick(
            x=constants.GAME_FIELD_SIZE[0]-constants.PLAYER_SIZE[0]
        )


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
        while collisions == None or len(collisions) > 0:
            # Find all possible collisions
            collisions = []
            for side in sides:
                collisions += collisionVectorSegment(
                    curStart, curEnd, side[0], side[1]
                )
            collisions += collisionBallBrick(
                self.ball, 
                self.playerBrick, 
                curMove
            )
            collisions += collisionBallBrick(
                self.ball, 
                self.enemyBrick, 
                curMove
            )
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
            minDist = collisionsDist[0]
            for i in range(1, len(collisions)):
                if collisionsDist[i] < minDist:
                    closestCollision = collisions[i]
                    minDist = collisionsDist[i]
            
            # Resolve the closest collision
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
        # No more collisions here
        curEnd = (
            curStart[0] + curMove[0],
            curStart[1] + curMove[1]
        )
        self.ball.xPos = curEnd[0]
        self.ball.yPos = curEnd[1]
        
