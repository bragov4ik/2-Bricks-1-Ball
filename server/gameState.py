from math import copysign
from typing import List
from enum import Enum
from functools import lru_cache

import library.utilities
import library.collisions
import library.constants
import library.customObjects


class GameState:
    ball: library.customObjects.Ball
    playerBrick: library.customObjects.Player
    enemyBrick: library.customObjects.Player
    playerScore: int
    enemyScore: int
    # Flags used to not check the same collision twice.
    # 4 sides : LEFT, UP, RIGHT, DOWN, player and enemy.  Needs to be
    # preserved between ticks
    collisionsResolved: List[bool]

    def __init__(self) -> None:
        self.ball = library.customObjects.Ball(
            x=library.constants.BALL_STARTING_POS[0],
            y=library.constants.BALL_STARTING_POS[1],
            scale=library.constants.BALL_RADIUS
        )
        self.ball.xVel = library.constants.BALL_STARTING_SPEED[0]
        self.ball.yVel = library.constants.BALL_STARTING_SPEED[1]
        self.playerBrick = library.customObjects.Player(
            xScale=library.constants.PLAYER_SIZE[0],
            yScale=library.constants.PLAYER_SIZE[1]
        )
        self.enemyBrick = library.customObjects.Player(
            x=library.constants.GAME_FIELD_SIZE[0]-library.constants.PLAYER_SIZE[0],
            xScale=library.constants.PLAYER_SIZE[0],
            yScale=library.constants.PLAYER_SIZE[1]
        )
        self.playerScore = 0
        self.enemyScore = 0
        self.collisionsResolved = [False]*6

    def tickState(self, t):
        # Players' moves
        for player in (self.playerBrick, self.enemyBrick):
            self.playersPhysics(player)
        self.ballPhysics(t)

    @lru_cache(maxsize=64)
    def generateSides(r):
        """
        Generates a tuple of segments representing field sides in the
        order LEFT, UP, RIGHT, DOWN
        """
        return (
            (
                (r, r),
                (r, r+library.constants.GAME_FIELD_SIZE[1])
            ),
            (
                (r, r),
                (-r+library.constants.GAME_FIELD_SIZE[0], r)
            ),
            (
                (-r+library.constants.GAME_FIELD_SIZE[0], r),
                (
                    -r+library.constants.GAME_FIELD_SIZE[0],
                    -r+library.constants.GAME_FIELD_SIZE[1]
                )
            ),
            (
                (r, -r+library.constants.GAME_FIELD_SIZE[1]),
                (
                    -r+library.constants.GAME_FIELD_SIZE[0],
                    -r+library.constants.GAME_FIELD_SIZE[1]
                )
            )
        )


    def ballPhysics(self, t):
        """
        Handles the ball's physics (moving forward, bouncing off the
        walls and bricks) + checks if it touched side walls (win 
        condition)
        """
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

        # LEFT, UP, RIGHT, DOWN. Cached method, no need to worry
        # about performance if the size is unchanged
        sides = GameState.generateSides(self.ball.xScale)
        
        collisionList: List[library.customObjects.Collision] = None
        # Indexes in collisionsResolved list of found collisions
        collisionsIDs: List[int] = []
        while (
            collisionList == None
            or (collisionList
                and library.utilities.distance(curStart, curEnd) != 0)    # Not magnitude of move!!!
        ):
            # Find all possible collisions
            collisionList = []
            collisionsIDs = []
            # Checking sides
            for i in range(len(sides)):
                if self.collisionsResolved[i]:
                    # Resolution of the collision skips only one
                    # iteration
                    self.collisionsResolved[i] = False
                    continue
                side = sides[i]
                newCollisions = library.collisions.collisionVectorSegment(
                    curStart, curEnd, side[0], side[1]
                )
                collisionList += newCollisions
                if newCollisions:
                    collisionsIDs += [i]*len(newCollisions)
            # Collisions with player1
            if self.collisionsResolved[4]:
                self.collisionsResolved[4] = False
            else:
                newCollisions = library.collisions.collisionBallBrick(
                    self.ball,
                    self.playerBrick,
                    curStart,
                    curMove
                )
                collisionList += newCollisions
                if newCollisions:
                    collisionsIDs += [4]*len(newCollisions)
            # Collisions with player2
            if self.collisionsResolved[5]:
                self.collisionsResolved[5] = False
            else:
                newCollisions = library.collisions.collisionBallBrick(
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
            closest = library.collisions.getClosestCollision(
                curStart,
                collisionList
            )
            if closest == None:
                # Must not happen as length check for 0 is not passed
                raise IndexError("No collisions to handle!")
            closestCollision = closest[0]
            closestCollisionID = collisionsIDs[closest[1]]

            # If the collision happens with the walls, update the score
            # and reset the game
            if closestCollisionID in (0, 2):
                winner: self.Players
                if closestCollisionID == 0:
                    # LEFT wall
                    winner = self.Players.PLAYER2
                elif closestCollisionID == 2:
                    # RIGHT wall
                    winner = self.Players.PLAYER1
                self.handleGoal(winner)
                return

            # Resolve the closest collision
            curMove = library.collisions.resolveCollision(
                curStart,
                curMove,
                closestCollision
            )
            curStart = closestCollision.position
            curEnd = (
                curStart[0] + curMove[0],
                curStart[1] + curMove[1]
            )
            (self.ball.xVel, self.ball.yVel) = library.utilities.mirrorVector2D(
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


    def playersPhysics(self, player):
        """
        Move the given player in such a way that it won't collide into
        the ball.  Instead it stops right before it (with a small gap).
        Motion is done according to the player's desiredMove field.
        """
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
        returnedVal = library.collisions.getClosestCollision(
            ballPos,
            library.collisions.collisionBallBrick(
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
                                library.constants.ERROR_MARGIN,
                                yPlayerMove
                            ))
            newPlayerMove = (
                0,
                yPlayerMove
            )
            player.moveBy(newPlayerMove[0], newPlayerMove[1])
            player.setDesiredMove(0.0, 0.0)
        

    def resetEntities(self):
        self.ball.xPos = library.constants.BALL_STARTING_POS[0]
        self.ball.yPos = library.constants.BALL_STARTING_POS[1]
        self.ball.xVel = library.constants.BALL_STARTING_SPEED[0]
        self.ball.yVel = library.constants.BALL_STARTING_SPEED[1]
        self.playerBrick.xPos = 0.0
        self.playerBrick.yPos = 0.0
        self.playerBrick.desiredMove[0] = 0.0
        self.playerBrick.desiredMove[1] = 0.0
        self.enemyBrick.xPos = (library.constants.GAME_FIELD_SIZE[0]
                                - library.constants.PLAYER_SIZE[0])
        self.enemyBrick.yPos = 0.0
        self.enemyBrick.desiredMove[0] = 0.0
        self.enemyBrick.desiredMove[1] = 0.0
        self.collisionsResolved = [False]*6

    
    class Players(Enum):
        PLAYER1 = 1
        PLAYER2 = 2


    def handleGoal(
        self,
        player: Players
    ):
        if player == self.Players.PLAYER1:
            self.playerScore += 1
        elif player == self.Players.PLAYER2:
            self.enemyScore += 1
        print("Score {}:{}".format(self.playerScore, self.enemyScore))
        self.resetEntities()
        