import pygame
import pygame.freetype

import client.eventHandler
import client.fieldRender
import client.gameState
import library.constants
import client.inputProcessing

class Game:
    quitGame: bool
    status: library.constants.GameStatus
    window: pygame.Surface
    fieldRenderer: client.fieldRender.PlayingFieldRenderer

    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        self.window = pygame.display.set_mode(
            library.constants.DEFAULT_RESOLUTION,
            pygame.RESIZABLE
        )
        self.fieldRenderer = client.fieldRender.PlayingFieldRenderer(
            self.window
        )
        self.clock = pygame.time.Clock()
        self.quitGame = False
        self.status = library.constants.GameStatus.RUNNING

        self.gameState = client.gameState.GameState()

        self.eventProcessor = client.eventHandler.EventHandler()
        self.mouseProcessor = client.inputProcessing.MouseInput(
            self.fieldRenderer,
            self.gameState.playerBrick
        )

        # Controls
        eventDict = self.eventProcessor.event_func_dict
        pressDict = self.eventProcessor.keydown_func_dict
        releaseDict = self.eventProcessor.keyup_func_dict

        pressDict[pygame.K_UP] = print
        eventDict[pygame.MOUSEMOTION] = self.mouseProcessor.playerMouseInput

    def processInput(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quitGame = True
            elif event.type != pygame.NOEVENT:
                self.eventProcessor.handleEvent(event)

        pygame.event.clear()

    def updateState(self):
        self.clock.tick(library.constants.TICK_RATE_LIMIT)
        if self.status == library.constants.GameStatus.RUNNING:
            self.gameState.tickState(self.clock.get_time())
        

    def render(self):
        if self.status == library.constants.GameStatus.RUNNING:
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

