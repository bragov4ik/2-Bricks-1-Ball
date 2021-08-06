import pygame
import pygame.freetype

import client.eventHandler
import client.fieldRender
import client.gameState
import client.inputProcessing
import library.constants

class Game:
    quit_game: bool
    status: library.constants.GameStatus
    window: pygame.Surface
    field_renderer: client.fieldRender.PlayingFieldRenderer

    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        self.window = pygame.display.set_mode(
            library.constants.DEFAULT_RESOLUTION,
            pygame.RESIZABLE
        )
        self.field_renderer = client.fieldRender.PlayingFieldRenderer(
            self.window
        )
        self.clock = pygame.time.Clock()
        self.quit_game = False
        self.status = library.constants.GameStatus.RUNNING

        self.game_state = client.gameState.GameState()

        self.event_processor = client.eventHandler.EventHandler()
        self.mouse_processor = client.inputProcessing.MouseInput(
            self.field_renderer,
            self.game_state.player_brick
        )

        # Controls
        event_dict = self.event_processor.event_func_dict
        press_dict = self.event_processor.keydown_func_dict
        release_dict = self.event_processor.keyup_func_dict

        press_dict[pygame.K_UP] = print
        event_dict[pygame.MOUSEMOTION] = self.mouse_processor.player_mouse_input

    def process_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game = True
            elif event.type != pygame.NOEVENT:
                self.event_processor.handle_event(event)

        pygame.event.clear()

    def update_state(self):
        self.clock.tick(library.constants.TICK_RATE_LIMIT)
        if self.status == library.constants.GameStatus.RUNNING:
            self.game_state.tick_state(self.clock.get_time())
        

    def render(self):
        if self.status == library.constants.GameStatus.RUNNING:
            # Draw field
            self.field_renderer.draw_background()
            self.field_renderer.draw_score(
                self.game_state.player_score,
                self.game_state.enemy_score
            )

            # Draw players
            self.game_state.player_brick.draw(self.field_renderer)
            self.game_state.enemy_brick.draw(self.field_renderer)

            # Draw the ball
            self.game_state.ball.draw(self.field_renderer)
        pygame.display.update()

    def run(self):
        while not self.quit_game:
            self.process_input()
            self.update_state()
            self.render()
        pygame.quit()

