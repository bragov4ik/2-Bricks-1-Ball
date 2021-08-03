import pygame
import pygame.freetype

import server.communicatinon
import server.gameState
import library.constants

class GameServer:
    quitGame: bool
    status: library.constants.GameStatus
    gameState: server.gameState.GameState
    clock: pygame.time.Clock
    connection: server.communicatinon.Communication

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.quitGame = False
        self.gameState = server.gameState.GameState()
        self.status = library.constants.GameStatus.PAUSE

        # Wait for 2 clients
        self.connection = server.communicatinon.Communication()
        self.connection.connectClients()
        
        self.status = library.constants.GameStatus.RUNNING
        

    def process_input(self):
        # get input from clients?
        pass

    def update_state(self):
        self.clock.tick(library.constants.TICK_RATE_LIMIT)
        if self.status == library.constants.GameStatus.RUNNING:
            self.gameState.tickState(self.clock.get_time())
        

    def render(self):
        # print something?
        pass


    def run(self):
        while not self.quitGame:
            self.process_input()
            self.update_state()
            self.render()
        pygame.quit()
