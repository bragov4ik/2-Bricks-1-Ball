import pygame
import pygame.freetype

import eventHandler
import fieldRender
import gameState
import constants
import inputProcessing

class Game:
    quitGame: bool
    status: constants.gameStatus
    window: pygame.Surface
    fieldRenderer: fieldRender.PlayingFieldRenderer

    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        self.window = pygame.display.set_mode(
            constants.DEFAULT_RESOLUTION,
            pygame.RESIZABLE
        )
        self.fieldRenderer = fieldRender.PlayingFieldRenderer(
            self.window
        )
        self.clock = pygame.time.Clock()
        self.quitGame = False
        self.status = constants.gameStatus.RUNNING

        self.gameState = gameState.GameState()

        self.eventHandler = eventHandler.EventHandler()
        self.mouseHandler = inputProcessing.MouseInput(
            self.fieldRenderer,
            self.gameState.playerBrick
        )

        # Controls
        eventDict = self.eventHandler.eventFuncDict
        pressDict = self.eventHandler.keyDownFuncDict
        releaseDict = self.eventHandler.keyUpFuncDict

        pressDict[pygame.K_UP] = print
        eventDict[pygame.MOUSEMOTION] = self.mouseHandler.playerMouseInput

    def processInput(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quitGame = True
            elif event.type != pygame.NOEVENT:
                self.eventHandler.handleEvent(event)

        pygame.event.clear()

    def updateState(self):
        self.clock.tick(constants.TICK_RATE_LIMIT)
        if self.status == constants.gameStatus.RUNNING:
            self.gameState.tickState(self.clock.get_time())
        

    def render(self):
        if self.status == constants.gameStatus.RUNNING:
            # Draw field
            self.fieldRenderer.drawBackground()
            self.fieldRenderer.drawScore(
                self.gameState.playerScore,
                self.gameState.enemyScore
            )

            # Draw players
            self.gameState.playerBrick.draw(self.fieldRenderer)
            self.gameState.enemyBrick.draw(self.fieldRenderer)

            # Draw the ball
            self.gameState.ball.draw(self.fieldRenderer)
        pygame.display.update()

    def run(self):
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()

