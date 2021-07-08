import constants

class GameState:
    ballPosition = [0.0, 0.0]
    ballPositionDiscrete = [0, 0]
    ballVelocity = [1, 1]
    playerPosition = 0
    enemyPosition = 0
    playerScore = 0
    enemyScore = 0

    def tickState(self, timePassed):
        # Move ball forward
        self.ballPosition[0] += self.ballVelocity[0] * timePassed * 1e-1
        self.ballPosition[1] += self.ballVelocity[1] * timePassed * 1e-1
        self.ballPositionDiscrete[0] = int(self.ballPosition[0])
        self.ballPositionDiscrete[1] = int(self.ballPosition[1])

        # Bounce back if required
        downOvershoot = self.ballPosition[0] + constants.BALL_RADIUS - constants.GAME_FIELD_SIZE[0]
        if downOvershoot > 0:
            self.ballPosition[0] -= 2*downOvershoot
            self.ballVelocity[0] *= -1
        upOvershoot = -(self.ballPosition[0] - constants.BALL_RADIUS)
        if upOvershoot > 0:
            self.ballPosition[0] += 2*upOvershoot
            self.ballVelocity[0] *= -1
        rightOvershoot = self.ballPosition[1] + constants.BALL_RADIUS - constants.GAME_FIELD_SIZE[1]
        if rightOvershoot > 0:
            self.ballPosition[1] -= 2*rightOvershoot
            self.ballVelocity[1] *= -1
        leftOvershoot = -(self.ballPosition[1] - constants.BALL_RADIUS)
        if leftOvershoot > 0:
            self.ballPosition[1] += 2*leftOvershoot
            self.ballVelocity[1] *= -1
        
        # TODO: detect collisions