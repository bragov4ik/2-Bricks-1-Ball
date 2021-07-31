from typing import List, Tuple, Union
import pygame
import pygame.freetype
from pygame import gfxdraw

import utilities
import constants


class PlayingFieldRenderer:
    window: pygame.Surface
    scoreFont: pygame.freetype.Font
    # Origin of field's borders to render them
    fieldRenderOrigin: Tuple[int, int]
    # Location of the actual playing field (to render playing objects
    # with offset)
    fieldOrigin: Tuple[int, int]
    borderColor: Tuple[int, int, int]
    backgroundColor: Tuple[int, int, int]

    def __init__(
        self,
        window,
        borderColor=(127, 234, 127),
        backgroundColor=(0, 0, 0),
        fontFile: Union[str, None] = None,
        fontSize: float = constants.SCORE_FONT_SIZE
    ) -> None:
        self.window = window
        self.scoreFont = pygame.freetype.Font(fontFile, size=fontSize)
        resolution = window.get_size()
        self.fieldOrigin = (
            (resolution[0] - constants.GAME_FIELD_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_SIZE[1]) / 2
        )
        self.fieldRenderOrigin = (
            (resolution[0] - constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_RENDER_SIZE[1]) / 2
        )
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor

    def updateOrigins(self):
        resolution = self.window.get_size()
        self.fieldOrigin = (
            (resolution[0] - constants.GAME_FIELD_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_SIZE[1]) / 2
        )
        self.fieldRenderOrigin = (
            (resolution[0] - constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_RENDER_SIZE[1]) / 2
        )

    def drawCircle(
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
        shiftedCenter = utilities.changeOrigin(
            center, self.fieldOrigin, (0, 0))
        shiftedCenter = tuple(map(int, shiftedCenter))
        radius = int(radius)
        gfxdraw.aacircle(
            self.window,
            shiftedCenter[0],
            shiftedCenter[1],
            radius,
            color
        )
        gfxdraw.filled_circle(
            self.window,
            shiftedCenter[0],
            shiftedCenter[1],
            radius,
            color
        )

    def drawLine(
        self,
        color,
        startPos,
        endPos,
        width=1
    ) -> pygame.Rect:
        """
        Draws a circle using pygame with the same parameters, except
        for shifted center according to playing field's coordinates.  
        Return value: see `pygame.draw.circle` docs
        """
        shiftedStart = utilities.changeOrigin(
            startPos, self.fieldOrigin, (0, 0))
        shiftedEnd = utilities.changeOrigin(endPos, self.fieldOrigin, (0, 0))
        pygame.draw.line(
            self.window,
            color,
            shiftedStart,
            shiftedEnd,
            width
        )

    def drawRect(
        self,
        color,
        rect: Tuple[int, int, int, int],
        width=0,
        borderRadius=0,
        borderTopLeftRadius=-1,
        borderTopRightRadius=-1,
        borderBottomLeftRadius=-1,
        borderBottomRightRadius=-1
    ) -> pygame.Rect:

        position = rect[:2]
        scale = rect[2:]
        shiftedPos = utilities.changeOrigin(position, self.fieldOrigin, (0, 0))
        newRect = tuple(shiftedPos) + scale
        pygame.draw.rect(
            self.window,
            color,
            newRect,
            width,
            borderRadius,
            borderTopLeftRadius,
            borderTopRightRadius,
            borderBottomLeftRadius,
            borderBottomRightRadius
        )

    def drawBackground(self):
        windowSize = self.window.get_size()
        pygame.draw.rect(
            self.window,
            self.backgroundColor,
            (
                0,
                0,
                windowSize[0],
                windowSize[1]
            )
        )
        pygame.draw.rect(
            self.window,
            self.borderColor,
            (
                self.fieldRenderOrigin[0],
                self.fieldRenderOrigin[1],
                constants.GAME_FIELD_RENDER_SIZE[0],
                constants.GAME_FIELD_RENDER_SIZE[1]
            )
        )
        pygame.draw.rect(
            self.window,
            self.backgroundColor,
            (
                self.fieldOrigin[0],
                self.fieldOrigin[1],
                constants.GAME_FIELD_SIZE[0],
                constants.GAME_FIELD_SIZE[1]
            )
        )


    def drawScore(self, playerScore, enemyScore):
        fontHeight = self.scoreFont.size
        if type(fontHeight) is Tuple[float, float]:
            # Maybe wrong?
            fontHeight = fontHeight[1]

        scoreTopCenter = (
            (self.fieldRenderOrigin[0]
            + constants.GAME_FIELD_RENDER_SIZE[0]/2),
            (self.fieldRenderOrigin[1]
            - fontHeight
            - constants.SCORE_OFFSET)
        )
        delimPos = (
            scoreTopCenter[0],
            scoreTopCenter[1] + 3
        )
        PlayingFieldRenderer.drawCentredText(
            self.scoreFont,
            self.window,
            delimPos,
            constants.SCORE_DELIMITER,
            fgcolor=constants.SCORE_FONT_COLOR
        )
        delimRect = self.scoreFont.get_rect(constants.SCORE_DELIMITER)
        delimWidth = delimRect.size[0]
        
        playerScoreStr = str(playerScore)
        playerScoreWidth = self.scoreFont.get_rect(
            playerScoreStr
        ).size[0]
        playerScorePos = (
            int(scoreTopCenter[0] - delimWidth/2.0 - playerScoreWidth - 2),
            int(scoreTopCenter[1])
        )
        self.scoreFont.render_to(
            self.window,
            playerScorePos,
            playerScoreStr, 
            fgcolor=constants.SCORE_FONT_COLOR,
            bgcolor=self.backgroundColor
        )

        enemyScoreStr = str(enemyScore)
        enemyScorePos = (
            scoreTopCenter[0] + delimWidth/2.0 + 2,
            scoreTopCenter[1]
        )
        self.scoreFont.render_to(
            self.window,
            enemyScorePos,
            enemyScoreStr,
            fgcolor=constants.SCORE_FONT_COLOR,
            bgcolor=self.backgroundColor
        )


    def drawCentredText(
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
        newPos = (
            dest[0] - width/2,
            dest[1]
        )
        font.render_to(
            surface,
            newPos,
            text,
            fgcolor,
            bgcolor,
            style,
            rotation,
            size
        )