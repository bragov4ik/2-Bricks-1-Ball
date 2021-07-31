from typing import Tuple, List
from abc import ABC, abstractmethod

import fieldRender


class MovableObject:
    xPos: float
    yPos: float
    xVel: float
    yVel: float

    def __init__(self):
        self.xPos, self.yPos = 0.0, 0.0
        self.xVel, self.yVel = 0.0, 0.0

    def moveBy(self, xMove, yMove):
        self.xPos += xMove
        self.yPos += yMove

    def moveTo(self, xNew, yNew):
        self.xPos = xNew
        self.yPos = yNew

    def __iter__(self):
        yield self.xPos
        yield self.yPos


class Collision:
    position: Tuple[float, float]
    normal: Tuple[float, float]

    def getUnitNormal(self) -> Tuple[float, float]:
        magnitude = (self.normal[0]**2 + self.normal[1]**2)**0.5
        return (
            self.normal[0]*magnitude,
            self.normal[1]*magnitude
        )


class Entity(MovableObject):
    color: Tuple[int, int, int]
    xScale: float
    yScale: float

    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
        self.xScale = 1.0
        self.yScale = 1.0

    @abstractmethod
    def draw(self, renderer: fieldRender.PlayingFieldRenderer):
        pass


class Ball(Entity):
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            scale: float = 10,
            color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__()
        # Assign each recieved value
        # Position - center of the ball
        self.xPos = x
        self.yPos = y
        self.xScale = scale
        self.yScale = scale
        self.color = color

    def draw(self, renderer: fieldRender.PlayingFieldRenderer):
        renderer.drawCircle(
            self.color,
            (self.xPos, self.yPos),
            self.xScale
        )


class Brick(Entity):
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            xScale: float = 10,
            yScale: float = 60,
            color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__()
        # Assign each recieved value
        # Brick's position shows upper left corner
        self.xPos = x
        self.yPos = y
        self.xScale = xScale
        self.yScale = yScale
        self.color = color

    def draw(self, renderer: fieldRender.PlayingFieldRenderer):
        renderer.drawRect(
            self.color,
            (
                self.xPos,
                self.yPos,
                self.xScale,
                self.yScale
            )
        )


class Player(Brick):
    # Used to move the player without colliding through the ball or
    # other objects
    desiredMove: List[float]

    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            xScale: float = 10,
            yScale: float = 60,
            color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y, xScale, yScale, color)
        self.desiredMove = [0.0, 0.0]

    def setDesiredMove(
        self,
        x: float,
        y: float
    ) -> None:
        """
        The player will attempt to move by this vector, however it will
        stop at the first collision along the move.
        """
        self.desiredMove[0] = x
        self.desiredMove[1] = y
