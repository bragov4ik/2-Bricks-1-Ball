from typing import List
import utilities
import collisions
import constants
import customObjects


class GameState:
    ball: customObjects.Ball
    playerBrick: customObjects.Brick
    enemyBrick: customObjects.Brick
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
        self.playerBrick = customObjects.Brick(
            xScale=constants.PLAYER_SIZE[0],
            yScale=constants.PLAYER_SIZE[1]
        )
        self.enemyBrick = customObjects.Brick(
            x=constants.GAME_FIELD_SIZE[0]-constants.PLAYER_SIZE[0],
            xScale=constants.PLAYER_SIZE[0],
            yScale=constants.PLAYER_SIZE[1]
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
            # Extract the one closest to the start (that does not
            # coincide with it to avoid handling one collision twice)
            collisionsDist = [
                utilities.distance(curStart, col.position) for col in collisionList
            ]
            # It is guaranteed that first entry exists as length check
            # for 0 is not passed
            closestCollision = collisionList[0]
            closestCollisionID = collisionsIDs[0]
            minDist = collisionsDist[0]
            for i in range(1, len(collisionList)):
                if collisionsDist[i] < minDist:
                    closestCollision = collisionList[i]
                    closestCollisionID = collisionsIDs[i]
                    minDist = collisionsDist[i]

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

        # # DEBUG
        # self.history.append((start, curEnd))
        # self.aboba += 1
        # if self.aboba >= 100:
        #     print("############################")
        #     print("Jumps (curVec.Start - prevVec.End) :")
        #     for i in range(1, len(self.history)):
        #         curVec = self.history[i]
        #         prevVec = self.history[i-1]
        #         diff = (curVec[0][0] - prevVec[1][0], curVec[0][1] - prevVec[1][1])
        #         #print("{}-{}={}".format(curVec[0], prevVec[1], diff))
        #         print(diff)
        # # \DEBUG

