from typing import Callable, Dict

import pygame


class EventHandler:
    """
    Class that handles the events by calling given functions when the
    events occur.  Can distinguish between different keys.
    """
    # Maps event types to their handlers.  Functions in value are
    # provided with the event recieved from pygame.
    eventFuncDict: Dict[
        int, Callable
    ]
    # Maps pressed key to a function
    keyDownFuncDict: Dict[
        int, Callable
    ]
    # Maps released key to a function
    keyUpFuncDict: Dict[
        int, Callable
    ]

    def __init__(self):
        self.eventFuncDict = {}
        self.keyDownFuncDict = {}
        self.keyUpFuncDict = {}
        self.eventFuncDict[pygame.KEYDOWN] = self.keyDown
        self.eventFuncDict[pygame.KEYUP] = self.keyUp

    def handleEvent(self, event):
        if event.type in self.eventFuncDict:
            self.eventFuncDict[event.type](event)

    def keyDown(self, event):
        key = event.__dict__["key"]
        if key in self.keyDownFuncDict:
            self.keyDownFuncDict[key](event)

    def keyUp(self, event):
        key = event.__dict__["key"]
        if key in self.keyUpFuncDict:
            self.keyUpFuncDict[key](event)
