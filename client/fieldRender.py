from typing import List, Tuple, Union
import pygame
import pygame.freetype
from pygame import gfxdraw

import library.utilities
import library.constants


class PlayingFieldRenderer:
    window: pygame.Surface
    score_font: pygame.freetype.Font
    # Origin of field's borders to render them
    field_render_origin: Tuple[int, int]
    # Location of the actual playing field (to render playing objects
    # with offset)
    field_origin: Tuple[int, int]
    border_color: Tuple[int, int, int]
    background_color: Tuple[int, int, int]

    def __init__(
        self,
        window,
        border_color=(127, 234, 127),
        background_color=(0, 0, 0),
        fontFile: Union[str, None] = None,
        fontSize: float = library.constants.SCORE_FONT_SIZE
    ) -> None:
        self.window = window
        self.score_font = pygame.freetype.Font(fontFile, size=fontSize)
        resolution = window.get_size()
        self.field_origin = (
            (resolution[0] - library.constants.GAME_FIELD_SIZE[0]) / 2,
            (resolution[1] - library.constants.GAME_FIELD_SIZE[1]) / 2
        )
        self.field_render_origin = (
            (resolution[0] - library.constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
            (resolution[1] - library.constants.GAME_FIELD_RENDER_SIZE[1]) / 2
        )
        self.border_color = border_color
        self.background_color = background_color

    def update_origins(self):
        resolution = self.window.get_size()
        self.field_origin = (
            (resolution[0] - library.constants.GAME_FIELD_SIZE[0]) / 2,
            (resolution[1] - library.constants.GAME_FIELD_SIZE[1]) / 2
        )
        self.field_render_origin = (
            (resolution[0] - library.constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
            (resolution[1] - library.constants.GAME_FIELD_RENDER_SIZE[1]) / 2
        )

    def draw_circle(
        self,
        color,
        center,
        radius
    ) -> pygame.Rect:
        """
        Draws a line using pygame with the same parameters, except
        for shifted positions according to playing field's coordinates.  
        Return value: see `pygame.draw.circle` docs
        """
        shifted_center = library.utilities.change_origin(
            center, self.field_origin, (0, 0))
        shifted_center = tuple(map(int, shifted_center))
        radius = int(radius)
        gfxdraw.aacircle(
            self.window,
            shifted_center[0],
            shifted_center[1],
            radius,
            color
        )
        gfxdraw.filled_circle(
            self.window,
            shifted_center[0],
            shifted_center[1],
            radius,
            color
        )

    def draw_line(
        self,
        color,
        start_pos,
        end_pos,
        width=1
    ) -> pygame.Rect:
        """
        Draws a circle using pygame with the same parameters, except
        for shifted center according to playing field's coordinates.  
        Return value: see `pygame.draw.circle` docs
        """
        shifted_start = library.utilities.change_origin(
            start_pos, self.field_origin, (0, 0))
        shifted_end = library.utilities.change_origin(end_pos, self.field_origin, (0, 0))
        pygame.draw.line(
            self.window,
            color,
            shifted_start,
            shifted_end,
            width
        )

    def draw_rect(
        self,
        color,
        rect: Tuple[int, int, int, int],
        width=0,
        border_radius=0,
        border_top_left_radius=-1,
        border_top_right_radius=-1,
        border_bottom_left_radius=-1,
        border_bottom_right_radius=-1
    ) -> pygame.Rect:

        position = rect[:2]
        scale = rect[2:]
        shifted_pos = library.utilities.change_origin(position, self.field_origin, (0, 0))
        new_rect = tuple(shifted_pos) + scale
        pygame.draw.rect(
            self.window,
            color,
            new_rect,
            width,
            border_radius,
            border_top_left_radius,
            border_top_right_radius,
            border_bottom_left_radius,
            border_bottom_right_radius
        )

    def draw_background(self):
        window_size = self.window.get_size()
        pygame.draw.rect(
            self.window,
            self.background_color,
            (
                0,
                0,
                window_size[0],
                window_size[1]
            )
        )
        pygame.draw.rect(
            self.window,
            self.border_color,
            (
                self.field_render_origin[0],
                self.field_render_origin[1],
                library.constants.GAME_FIELD_RENDER_SIZE[0],
                library.constants.GAME_FIELD_RENDER_SIZE[1]
            )
        )
        pygame.draw.rect(
            self.window,
            self.background_color,
            (
                self.field_origin[0],
                self.field_origin[1],
                library.constants.GAME_FIELD_SIZE[0],
                library.constants.GAME_FIELD_SIZE[1]
            )
        )


    def draw_score(self, player_score, enemy_score):
        font_height = self.score_font.size
        if type(font_height) is Tuple[float, float]:
            # Maybe wrong?
            font_height = font_height[1]

        score_top_center = (
            (self.field_render_origin[0]
            + library.constants.GAME_FIELD_RENDER_SIZE[0]/2),
            (self.field_render_origin[1]
            - font_height
            - library.constants.SCORE_OFFSET)
        )
        delim_pos = (
            score_top_center[0],
            score_top_center[1] + 3
        )
        PlayingFieldRenderer.draw_centred_text(
            self.score_font,
            self.window,
            delim_pos,
            library.constants.SCORE_DELIMITER,
            fgcolor=library.constants.SCORE_FONT_COLOR
        )
        delim_rect = self.score_font.get_rect(library.constants.SCORE_DELIMITER)
        delim_width = delim_rect.size[0]
        
        player_score_str = str(player_score)
        player_score_width = self.score_font.get_rect(
            player_score_str
        ).size[0]
        player_score_pos = (
            int(score_top_center[0] - delim_width/2.0 - player_score_width - 2),
            int(score_top_center[1])
        )
        self.score_font.render_to(
            self.window,
            player_score_pos,
            player_score_str, 
            fgcolor=library.constants.SCORE_FONT_COLOR,
            bgcolor=self.background_color
        )

        enemy_score_str = str(enemy_score)
        enemy_score_pos = (
            score_top_center[0] + delim_width/2.0 + 2,
            score_top_center[1]
        )
        self.score_font.render_to(
            self.window,
            enemy_score_pos,
            enemy_score_str,
            fgcolor=library.constants.SCORE_FONT_COLOR,
            bgcolor=self.background_color
        )


    def draw_centred_text(
        font: pygame.freetype.Font,
        surface: pygame.Surface,
        dest: Tuple[float, float],
        text: str,
        fgcolor: Tuple[int, int, int] = (255, 255, 255),
        bgcolor: Tuple[int, int, int] = (0, 0, 0),
        style: int = pygame.freetype.STYLE_DEFAULT,
        rotation: int = 0,
        size: float = 0
    ):
        width = font.get_rect(text).size[0]
        new_pos = (
            dest[0] - width/2,
            dest[1]
        )
        font.render_to(
            surface,
            new_pos,
            text,
            fgcolor,
            bgcolor,
            style,
            rotation,
            size
        )