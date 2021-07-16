from typing import Tuple
import pygame
import math

from pygame.constants import NOEVENT
import render
import gameState
import constants

class Game:
    quitGame: bool
    window: pygame.Surface
    fieldRenderer: render.PlayingFieldRenderer

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(
            constants.DEFAULT_RESOLUTION,
            pygame.RESIZABLE
        )
        self.fieldRenderer = render.PlayingFieldRenderer(
            self.window
        )
        self.clock = pygame.time.Clock()
        self.quitGame = False

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
    
    def render(self):
        # Draw background
        self.fieldRenderer.drawBackground()

        # Draw players
        self.game_state.playerBrick.draw(self.fieldRenderer)
        self.game_state.enemyBrick.draw(self.fieldRenderer)

        # Draw the ball
        self.game_state.ball.draw(self.fieldRenderer)

        pygame.display.update()

    def run(self):
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()
        

game = Game()
game.run()
