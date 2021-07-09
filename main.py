import pygame
import math

from pygame.constants import NOEVENT
import gameState
import constants

class Game:
    quitGame = False
    resolution = (640, 480)

    # Position at the center, actual inside rendered
    # (prolly need to move these details in some render class (or smth)?)
    fieldRenderOrigin = (
        (resolution[0] - constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
        (resolution[1] - constants.GAME_FIELD_RENDER_SIZE[1]) / 2
    )
    fieldOrigin = (
        (resolution[0] - constants.GAME_FIELD_SIZE[0]) / 2,
        (resolution[1] - constants.GAME_FIELD_SIZE[1]) / 2
    )

    def init(self):
        pygame.init()
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.color_state = 0

        self.game_state = gameState.GameState()

    def processInput(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.quitGame = True
        elif event.type != pygame.NOEVENT:
            print(event)
    
    def updateState(self):
        self.clock.tick(constants.TICK_RATE_LIMIT)
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
        pygame.draw.rect(
            self.window, 
            self.color, 
            (
                self.fieldRenderOrigin[0],
                self.fieldRenderOrigin[1], 
                constants.GAME_FIELD_RENDER_SIZE[0],
                constants.GAME_FIELD_RENDER_SIZE[1]
            )
        )

        # Draw players
        pygame.draw.rect(
            self.window, 
            (255, 255, 255), 
            (
                self.fieldOrigin[0], 
                self.fieldOrigin[1] + self.game_state.playerPosition, 
                constants.PLAYER_SIZE[0], 
                constants.PLAYER_SIZE[1]
            )
        )
        pygame.draw.rect(
            self.window, 
            (255, 255, 255), 
            (
                (self.fieldOrigin[0] + constants.GAME_FIELD_SIZE[0]) - constants.PLAYER_SIZE[0], 
                self.fieldOrigin[1] + self.game_state.enemyPosition, 
                constants.PLAYER_SIZE[0], 
                constants.PLAYER_SIZE[1]
            )
        )

        # Draw the ball
        pygame.draw.circle(
            self.window, 
            (255, 255, 255), 
            (
                self.fieldOrigin[0] + self.game_state.ballPosition[0], 
                self.fieldOrigin[1] + self.game_state.ballPosition[1]
            ),
            constants.BALL_RADIUS
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