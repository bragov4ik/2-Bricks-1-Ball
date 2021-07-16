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
        self.ball = objects.Ball()
        self.ball.xVel = 1
        self.ball.yVel = 1
        self.playerBrick = objects.Brick()
        self.enemyBrick = objects.Brick(
            x=constants.GAME_FIELD_SIZE[0]-constants.PLAYER_SIZE[0]
            )


    def tickState(self, t):
        # Move ball forward
        self.ball.moveBy(
            self.ball.xVel*t*1e-1, 
            self.ball.yVel*t*1e-1
        )

        # Bounce back if required
        downOvershoot = (self.ball.yPos
                         + constants.BALL_RADIUS
                         - constants.GAME_FIELD_SIZE[1])
        if downOvershoot > 0:
            self.ball.yPos -= 2*downOvershoot
            self.ball.yVel *= -1
        upOvershoot = -(self.ball.yPos - constants.BALL_RADIUS)
        if upOvershoot > 0:
            self.ball.yPos += 2*upOvershoot
            self.ball.yVel *= -1
        rightOvershoot = (self.ball.xPos
                             + constants.BALL_RADIUS
                             - constants.GAME_FIELD_SIZE[0])
        if rightOvershoot > 0:
            self.ball.xPos -= 2*rightOvershoot
            self.ball.xVel *= -1
        leftOvershoot = -(self.ball.xPos - constants.BALL_RADIUS)
        if leftOvershoot > 0:
            self.ball.xPos += 2*leftOvershoot
            self.ball.xVel *= -1

        # TODO: detect collisions
