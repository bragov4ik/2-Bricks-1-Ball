from typing import Tuple, List
from abc import ABC, abstractmethod

import pygame
import library.utilities
import library.collisions


class MovableObject(ABC):
    def __init__(self):
        self.location = [0, 0]

    @abstractmethod
    def move_by(self, move):
        pass

    @abstractmethod
    def move_to(self, new_location):
        pass

    def __iter__(self):
        yield self.location[0]
        yield self.location[1]


class Point(MovableObject):
    def __init__(self, x: float, y: float):
        self.location = [x, y]

    def moveBy(self, move: List[float]):
        self.location[0] += move[0]
        self.location[1] += move[1]

    def moveTo(self, new_location: List[float]):
        self.location[0] = new_location[0]
        self.location[1] = new_location[1]


class Figure(ABC):
    def __init__(self):
        self.color = (0, 0, 0)

    @abstractmethod
    def draw(self, window):
        pass


class Circle(Figure):
    def __init__(
            self,
            center: Point = Point(100, 100),
            r: float = 100,
            color: Tuple[int, int, int] = (200, 128, 200)):
        self.center = center
        self.radius = r
        self.color = color

    def draw(self, window):
        pygame.draw.circle(
            window,
            self.color,
            tuple(self.center),
            self.radius
        )


class Segment(Figure):
    def __init__(
            self,
            start: Point,
            end: Point,
            color: Tuple[int, int, int] = (200, 200, 200),
            thickness: int = 2):
        self.start = start
        self.end = end
        self.color = color
        self.thickness = thickness

    def draw(self, window):
        pygame.draw.line(
            window,
            self.color,
            tuple(self.start),
            tuple(self.end),
            self.thickness
        )


class InputHandler:
    def __init__(
        self,
        controllable_object: MovableObject,
        control_keys: Tuple[int, int, int, int]
    ):
        self.controllable_object = controllable_object
        self.control_keys = control_keys
        # All keys are released by default
        self.pressed_keys = [
            False,
            False,
            False,
            False
        ]

    # List of 4 boolean variables indicating if corresponding control
    # key is considered pressed
    pressed_keys = list()
    # Control keys is a 4 element tuple of keys assigned for
    # y pos, x pos, y neg, and x neg moves respectively (1 step in
    # positive/negative direction of the axis)
    control_keys = (0, 0, 0, 0)
    # Timer used for precise controls (has delay before rapid update)
    # 0 if nothing was pressed on previous update
    press_start_time = 0

    def handle_key_down(
        self,
        pressed_key: int
    ):
        try:
            key_index = self.control_keys.index(pressed_key)
            self.pressed_keys[key_index] = True
        except ValueError:
            # Key does not belong to the list of specified control keys.
            pass

    def handle_key_up(
        self,
        released_key: int
    ):
        try:
            key_index = self.control_keys.index(released_key)
            self.pressed_keys[key_index] = False

            # Reset move timer if all are released now
            all_released = True
            for key in self.pressed_keys:
                if key:
                    all_released = False
            if all_released:
                self.press_start_time = 0
        except ValueError as verr:
            # Key does not belong to the list of specified control keys.
            pass

    def move_object(self):
        """
        Moves the controlled object according to captured input.  Has
        500 ms delay between pressing and rapid movement of the object.
        Returns whether anything was updated.
        """
        was_updated = False
        if (pygame.time.get_ticks() - self.press_start_time < 500
                and self.press_start_time != 0):
            # Don't move if cooldown is not over yet
            return False

        move = [0, 0]
        if self.pressed_keys[0]:
            move[1] += 1
            was_updated = True
        if self.pressed_keys[1]:
            move[0] += 1
            was_updated = True
        if self.pressed_keys[2]:
            move[1] -= 1
            was_updated = True
        if self.pressed_keys[3]:
            move[0] -= 1
            was_updated = True
        # Start timer if needed
        if was_updated and self.press_start_time == 0:
            self.press_start_time = pygame.time.get_ticks()
        if was_updated:
            self.controllable_object.move_by(move)
        return was_updated


class Game:
    # Constants?
    COLOR_BACKGRND = (255, 128, 0)
    RADIUS_COLLISION = 3
    COLOR_COLLISION = (240, 240, 230)

    # Variables
    quit_game: bool
    updaters: List[InputHandler]
    figures: List[Figure]
    collisions: List[Figure]

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.updaters = []
        self.figures = []
        self.collisions = []
        self.quit_game = False

    def process_input(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.quit_game = True
        elif event.type == pygame.KEYDOWN:
            key = event.__dict__["key"]
            for updater in self.updaters:
                updater.handle_key_down(key)
        elif event.type == pygame.KEYUP:
            key = event.__dict__["key"]
            for updater in self.updaters:
                updater.handle_key_up(key)

    def tick_updaters(self):
        """
        Moves all objects attached to updaters accordingly.  Return
        whether anything was actually changed
        """
        any_updated = False
        for updater in self.updaters:
            was_moved = updater.move_object()
            if was_moved:
                any_updated = True
        return any_updated

    def reinit_collisions(self):
        pass

    def update_state(self):
        self.clock.tick(60)
        any_updated = self.tick_updaters()
        if any_updated:
            self.reinit_collisions()

    def render(self):
        # Draw background

        pygame.draw.rect(
            self.window,
            self.COLOR_BACKGRND,
            (0, 0) + pygame.display.get_window_size()
        )

        for figure in self.figures:
            figure.draw(self.window)
        for figure in self.collisions:
            figure.draw(self.window)

        pygame.display.update()

    def run(self):
        while not self.quit_game:
            self.process_input()
            self.update_state()
            self.render()
        pygame.quit()


class DemoSegCirc(Game):
    def __init__(self):
        super().__init__()
        self.circle = Circle(Point(250, 250), 100)

        self.segment = Segment(
            Point(100, 100),
            Point(400, 200)
        )

        self.segment_updater1 = InputHandler(
            self.segment.start,
            (
                pygame.K_DOWN,
                pygame.K_RIGHT,
                pygame.K_UP,
                pygame.K_LEFT
            )
        )
        self.segment_updater2 = InputHandler(
            self.segment.end,
            (
                pygame.K_s,
                pygame.K_d,
                pygame.K_w,
                pygame.K_a
            )
        )
        self.updaters: List[InputHandler] = [
            self.segment_updater1,
            self.segment_updater2,
        ]
        self.figures: List[Figure] = [
            self.circle,
            self.segment,
        ]
        # Need to initialize collisions as we've just added figures
        self.reinit_collisions()

    def reinit_collisions(self):
        collisions = library.collisions.collision_vector_circle(
            self.segment.start.location,
            self.segment.end.location,
            self.circle.center.location,
            self.circle.radius
        )
        self.collisions = []
        for col in collisions:
            # Don't draw if outside the segment
            if not library.utilities.point_in_box(
                col,
                self.segment.start.location,
                self.segment.end.location
            ):
                continue

            colFig = Circle(
                Point(col[0], col[1]),
                self.RADIUS_COLLISION,
                self.COLOR_COLLISION
            )
            self.collisions.append(colFig)

    circle: Circle
    segment: Segment
    segment_updater1: InputHandler
    segment_updater2: InputHandler


class Demo2Seg(Game):
    def __init__(self):
        super().__init__()
        self.segment1 = Segment(Point(0, 0), Point(100, 100))
        self.segment2 = Segment(Point(100, 0), Point(0, 100))

        self.segment_updater1 = InputHandler(
            self.segment1.start,
            (
                pygame.K_s,
                pygame.K_d,
                pygame.K_w,
                pygame.K_a
            )
        )
        self.segment_updater2 = InputHandler(
            self.segment1.end,
            (
                pygame.K_k,
                pygame.K_l,
                pygame.K_i,
                pygame.K_j
            )
        )

        self.segment_updater3 = InputHandler(
            self.segment2.start,
            (
                pygame.K_DOWN,
                pygame.K_RIGHT,
                pygame.K_UP,
                pygame.K_LEFT
            )
        )
        self.segment_updater4 = InputHandler(
            self.segment2.end,
            (
                pygame.K_KP2,
                pygame.K_KP6,
                pygame.K_KP8,
                pygame.K_KP4
            )
        )

        self.updaters: List[InputHandler] = [
            self.segment_updater1,
            self.segment_updater2,
            self.segment_updater3,
            self.segment_updater4,
        ]
        self.figures: List[Figure] = [
            self.segment1,
            self.segment2,
        ]
        self.reinit_collisions()

    def reinit_collisions(self):
        collisions = library.collisions.collision_vector_segment(
            vecStart=self.segment1.start.location,
            vecEnd=self.segment1.end.location,
            segStart=self.segment2.start.location,
            segEnd=self.segment2.end.location
        )

        self.collisions = []
        for col in collisions:
            colFig = Circle(
                Point(col[0], col[1]),
                self.RADIUS_COLLISION,
                self.COLOR_COLLISION
            )
            self.collisions.append(colFig)

    segment1: Segment
    segment2: Segment
    segment_updater1: InputHandler
    segment_updater2: InputHandler
    segment_updater3: InputHandler
    segment_updater4: InputHandler


game = DemoSegCirc()
game.run()
