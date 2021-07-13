from typing import Tuple, List
import pygame
import utilities
from abc import ABC, abstractmethod


class MovableObject(ABC):
    def __init__(self):
        self.location = [0, 0]


    @abstractmethod
    def moveBy(self, move):
        pass


    @abstractmethod
    def moveTo(self, newLocation):
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
    

    def moveTo(self, newLocation: List[float]):
        self.location[0] = newLocation[0]
        self.location[1] = newLocation[1]


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
        controllableObject: MovableObject,
        controlKeys: Tuple[int, int, int, int]
        ):
        self.controllableObject = controllableObject
        self.controlKeys = controlKeys
        # All keys are released by default
        self.pressedKeys = [
            False, 
            False, 
            False, 
            False 
        ]


    # List of 4 boolean variables indicating if corresponding control
    # key is considered pressed
    pressedKeys = list()
    # Control keys is a 4 element tuple of keys assigned for
    # y pos, x pos, y neg, and x neg moves respectively (1 step in 
    # positive/negative direction of the axis)
    controlKeys = (0, 0, 0, 0)
    # Timer used for precise controls (has delay before rapid update)
    # 0 if nothing was pressed on previous update
    pressStartTime = 0

    def handleKeyDown(
        self,
        pressedKey: int
        ):
        try:
            keyIndex = self.controlKeys.index(pressedKey)
            self.pressedKeys[keyIndex] = True
        except ValueError:
            # Key does not belong to the list of specified control keys.
            pass


    def handleKeyUp(
        self,
        releasedKey: int
        ):
        try:
            keyIndex = self.controlKeys.index(releasedKey)
            self.pressedKeys[keyIndex] = False

            # Reset move timer if all are released now
            allReleased = True
            for key in self.pressedKeys:
                if key:
                    allReleased = False
            if allReleased:
                self.pressStartTime = 0
        except ValueError as verr:
            # Key does not belong to the list of specified control keys.
            pass


    def moveObject(self):
        """
        Moves the controlled object according to captured input.  Has
        500 ms delay between pressing and rapid movement of the object.
        Returns whether anything was updated.
        """
        wasUpdated = False
        if (pygame.time.get_ticks() - self.pressStartTime < 500
            and self.pressStartTime != 0):
            # Don't move if cooldown is not over yet
            return False
        
        move = [0, 0]
        if self.pressedKeys[0]:
            move[1] += 1
            wasUpdated = True
        if self.pressedKeys[1]:
            move[0] += 1
            wasUpdated = True
        if self.pressedKeys[2]:
            move[1] -= 1
            wasUpdated = True
        if self.pressedKeys[3]:
            move[0] -= 1
            wasUpdated = True
        # Start timer if needed
        if wasUpdated and self.pressStartTime == 0:
            self.pressStartTime = pygame.time.get_ticks()
        if wasUpdated:
            self.controllableObject.moveBy(move)
        return wasUpdated


class Game:
    quitGame = False
    colorBackgr = (255, 128, 0)

    circle = Circle(Point(250, 250), 100)

    lineUpdated = True
    segment = Segment(
        Point(100, 100),
        Point(400, 200)
    )

    collisions = []
    radiusCollision = 3
    colorCollision = (240, 240, 230)

    segmentUpdater1 = InputHandler(
        segment.start,
        (
            pygame.K_DOWN,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_LEFT
        )
    )
    segmentUpdater2 = InputHandler(
        segment.end,
        (
            pygame.K_s,
            pygame.K_d,
            pygame.K_w,
            pygame.K_a
        )
    )
    updaters: List[InputHandler] = [
        segmentUpdater1, 
        segmentUpdater2,
    ]

    figures: List[Figure] = [
        circle,
        segment
    ]

    def init(self):
        pygame.init()
        self.window = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

    def processInput(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.quitGame = True
        elif event.type == pygame.KEYDOWN:
            key = event.__dict__["key"]
            for updater in self.updaters:
                updater.handleKeyDown(key)
        elif event.type == pygame.KEYUP:
            key = event.__dict__["key"]
            for updater in self.updaters:
                updater.handleKeyUp(key)

    def updateState(self):
        self.clock.tick(60)
        for updater in self.updaters:
            wasMoved = updater.moveObject()
            if wasMoved:
                self.lineUpdated = True

        if self.lineUpdated:
            collisions = utilities.collisionLineCircle(
                self.segment.start.location, 
                self.segment.end.location, 
                self.circle.center.location, 
                self.circle.radius
            )
            self.collisions = []
            self.figures = [
                self.circle,
                self.segment
            ]
            for col in collisions:
                # Don't draw if outside the segment
                if not utilities.pointInBox(
                    col, 
                    self.segment.start.location, 
                    self.segment.end.location
                    ):
                    continue

                colFig = Circle(
                    Point(col[0], col[1]),
                    self.radiusCollision,
                    self.colorCollision
                )
                self.collisions.append(colFig)
                self.figures.append(colFig)
            self.lineUpdated = False

    def render(self):
        # Draw background

        pygame.draw.rect(
            self.window,
            self.colorBackgr,
            (0, 0) + pygame.display.get_window_size()
        )
        
        for figure in self.figures:
            figure.draw(self.window)

        pygame.display.update()

    def run(self):
        self.init()
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()


game = Game()
game.run()
