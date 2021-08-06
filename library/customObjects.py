from typing import Tuple, List
from abc import ABC, abstractmethod

import client.fieldRender


class MovableObject:
    x_pos: float
    y_pos: float
    x_vel: float
    y_vel: float

    def __init__(self):
        self.x_pos, self.y_pos = 0.0, 0.0
        self.x_vel, self.y_vel = 0.0, 0.0

    def move_by(self, x_move, y_move):
        self.x_pos += x_move
        self.y_pos += y_move

    def moveTo(self, x_new, y_new):
        self.x_pos = x_new
        self.y_pos = y_new

    def __iter__(self):
        yield self.x_pos
        yield self.y_pos


class Collision:
    position: Tuple[float, float]
    normal: Tuple[float, float]

    def get_unit_normal(self) -> Tuple[float, float]:
        magnitude = (self.normal[0]**2 + self.normal[1]**2)**0.5
        return (
            self.normal[0]*magnitude,
            self.normal[1]*magnitude
        )


class Entity(MovableObject):
    color: Tuple[int, int, int]
    x_scale: float
    y_scale: float

    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
        self.x_scale = 1.0
        self.y_scale = 1.0

    @abstractmethod
    def draw(self, renderer: client.fieldRender.PlayingFieldRenderer):
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
        self.x_pos = x
        self.y_pos = y
        self.x_scale = scale
        self.y_scale = scale
        self.color = color

    def draw(self, renderer: client.fieldRender.PlayingFieldRenderer):
        renderer.draw_circle(
            self.color,
            (self.x_pos, self.y_pos),
            self.x_scale
        )


class Brick(Entity):
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            x_scale: float = 10,
            y_scale: float = 60,
            color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__()
        # Assign each recieved value
        # Brick's position shows upper left corner
        self.x_pos = x
        self.y_pos = y
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.color = color

    def draw(self, renderer: client.fieldRender.PlayingFieldRenderer):
        renderer.draw_rect(
            self.color,
            (
                self.x_pos,
                self.y_pos,
                self.x_scale,
                self.y_scale
            )
        )


class Player(Brick):
    # Used to move the player without colliding through the ball or
    # other objects
    desired_move: List[float]

    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            x_scale: float = 10,
            y_scale: float = 60,
            color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y, x_scale, y_scale, color)
        self.desired_move = [0.0, 0.0]

    def set_desired_move(
        self,
        x: float,
        y: float
    ) -> None:
        """
        The player will attempt to move by this vector, however it will
        stop at the first collision along the move.
        """
        self.desired_move[0] = x
        self.desired_move[1] = y
