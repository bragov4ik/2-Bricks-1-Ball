import pygame
import pygame.freetype

import server.communication
import server.gameState
import library.constants

class GameServer:
    quit_game: bool
    status: library.constants.GameStatus
    game_state: server.gameState.GameState
    clock: pygame.time.Clock
    connection: server.communication.Communication

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.quit_game = False
        self.game_state = server.gameState.GameState()
        self.status = library.constants.GameStatus.PAUSE

        # Wait for 2 clients
        self.connection = server.communication.Communication()
        
        self.status = library.constants.GameStatus.RUNNING
        

    def process_input(self):
        # get input from clients?
        pass

    def update_state(self):
        self.clock.tick(library.constants.TICK_RATE_LIMIT)
        if self.status == library.constants.GameStatus.RUNNING:
            self.game_state.tick_state(self.clock.get_time())
        

    def render(self):
        # print something?
        pass


    def run(self):
        while not self.quit_game:
            self.process_input()
            self.update_state()
            self.render()
        pygame.quit()
