import constants

class GameState:
    ballPosition = [0, 0]
    ballVelocity = [1, 1]
    playerPosition = 0
    enemyPosition = 0
    playerScore = 0
    enemyScore = 0

    def tickState(self, timePassed):
        # Move ball forward
        self.ballPosition[0] += self.ballVelocity[0] * timePassed
        self.ballPosition[1] += self.ballVelocity[1] * timePassed
        
        # TODO: detect collisions