import pygame
import math
import gameState
import constants

class Game:
    quitGame = False
    resolution = (640, 480)

    def init(self):
        pygame.init()
        self.window = pygame.display.set_mode((640,480))
        self.clock = pygame.time.Clock()
        self.color_state = 0

        self.game_state = gameState.GameState()

    def processInput(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.quitGame = True
    
    def updateState(self):
        self.clock.tick(60)
        self.game_state.tickState(self.clock.get_time())

        self.color_state += 8e-3 * self.clock.get_time()
        if self.color_state > 2 * math.pi:
            self.color_state -= 2 * math.pi
        color_R = int(127 * math.cos(self.color_state)) + 127
        color_G = int(127 * math.sin(self.color_state)) + 127
        color_B = int((color_R + color_G) / 2)
        self.color = (color_R, color_G, color_B)
    
    def render(self):
        # Draw background
        pygame.draw.rect(self.window, self.color, (0, 0, 640, 480))

        # Draw players
        pygame.draw.rect(
            self.window, 
            (255, 255, 255), 
            (
                0, 
                self.game_state.playerPosition, 
                constants.playerSize[0], 
                constants.playerSize[1]
            )
        )
        pygame.draw.rect(
            self.window, 
            (255, 255, 255), 
            (
                self.resolution[0] - constants.playerSize[0], 
                self.game_state.enemyPosition, 
                constants.playerSize[0], 
                constants.playerSize[1]
            )
        )

        # Draw the ball
        pygame.draw.circle(
            self.window, 
            (255, 255, 255), 
            (
                self.game_state.ballPosition[0], 
                self.game_state.ballPosition[1]
            ),
            constants.ballRadius
        )
        pygame.display.update()

    def run(self):
        self.init()
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()
        

game = Game()
game.run()