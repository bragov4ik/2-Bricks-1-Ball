import pygame
import constants
from typing import List, Tuple


class PlayingFieldRenderer:
    window: pygame.Surface
    # Origin of field's borders to render them
    fieldRenderOrigin: Tuple[int, int]
    # Location of the actual playing field (to render playing objects
    # with offset)
    fieldOrigin: Tuple[int, int]
    backgroundColor: Tuple[int, int, int]

    def __init__(
        self,
        window,
        backgroundColor=(127, 234, 127)
    ) -> None:
        self.window = window
        resolution = window.get_size()
        self.fieldOrigin = (
            (resolution[0] - constants.GAME_FIELD_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_SIZE[1]) / 2
        )
        self.fieldRenderOrigin = (
            (resolution[0] - constants.GAME_FIELD_RENDER_SIZE[0]) / 2,
            (resolution[1] - constants.GAME_FIELD_RENDER_SIZE[1]) / 2
        )
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

    def __shiftCoordinates(self, coords):
        """
        Shifts any iterable coordinates by `fieldOrigin`
        """
        newCoords = []
        for coord, offset in zip(coords, self.fieldOrigin):
            newCoords.append(coord+offset)
        # If the specified origin had less dimensions, leave remaining
        # ones unchanged
        if len(newCoords) < len(coords):
            newCoords.extend(coords[len(newCoords):])
        return newCoords

    def drawCircle(
        self,
        color,
        center,
        radius,
        width=0,
        drawTopRight=False,
        drawTopLeft=False,
        drawBottomLeft=False,
        drawBottomRight=False
    ) -> pygame.Rect:
        """
        Draws a line using pygame with the same parameters, except
        for shifted positions according to playing field's coordinates.  
        Return value: see `pygame.draw.circle` docs
        """
        shiftedCenter = self.__shiftCoordinates(center)
        pygame.draw.circle(
            self.window,
            color,
            shiftedCenter,
            radius,
            width,
            drawTopRight,
            drawTopLeft,
            drawBottomLeft,
            drawBottomRight
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
        shiftedStart = self.__shiftCoordinates(startPos)
        shiftedEnd = self.__shiftCoordinates(endPos)
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
        shiftedPos = self.__shiftCoordinates(position)
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
        pygame.draw.rect(
            self.window,
            self.backgroundColor,
            (
                self.fieldRenderOrigin[0],
                self.fieldRenderOrigin[1],
                constants.GAME_FIELD_RENDER_SIZE[0],
                constants.GAME_FIELD_RENDER_SIZE[1]
            )
        )
