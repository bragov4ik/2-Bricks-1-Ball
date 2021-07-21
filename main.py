from typing import Tuple
import pygame
import math

from pygame.constants import NOEVENT
import render
import gameState
import constants
import utilities

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

        # Draw the stadium for debugging
        stad = utilities.brickBallToStadium(
            self.game_state.ball,
            self.game_state.enemyBrick
        )
        # sides
        for side in [
            stad.leftSide, 
            stad.rightSide, 
            stad.topSide, 
            stad.bottomSide
        ]:
            self.fieldRenderer.drawLine((100, 0, 0), side[0], side[1])
        # corner circles
        for corner in [
            stad.leftTopCorner, 
            stad.rightTopCorner, 
            stad.leftBottomCorner, 
            stad.rightBottomCorner
        ]:
            self.fieldRenderer.drawCircle((100, 0, 0), corner[0], corner[1], 1)

        # corner boxes
        for corner in [
            stad.leftTopCornerBox, 
            stad.rightTopCornerBox,
            stad.leftBottomCornerBox, 
            stad.rightBottomCornerBox
        ]:
            self.fieldRenderer.drawLine((100, 0, 0), corner[0], corner[1])

        pygame.display.update()

    def run(self):
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()
        

game = Game()
game.run()
