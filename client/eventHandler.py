from typing import Callable, Dict

import pygame


class EventHandler:
    """
    Class that handles the events by calling given functions when the
    events occur.  Can distinguish between different keys.
    """
    # Maps event types to their handlers.  Functions in value are
    # provided with the event recieved from pygame.
    event_func_dict: Dict[
        int, Callable
    ]
    # Maps pressed key to a function
    keydown_func_dict: Dict[
        int, Callable
    ]
    # Maps released key to a function
    keyup_func_dict: Dict[
        int, Callable
    ]

    def __init__(self):
        self.event_func_dict = {}
        self.keydown_func_dict = {}
        self.keyup_func_dict = {}
        self.event_func_dict[pygame.KEYDOWN] = self.keyDown
        self.event_func_dict[pygame.KEYUP] = self.keyUp

    def handle_event(self, event):
        if event.type in self.event_func_dict:
            self.event_func_dict[event.type](event)

    def key_down(self, event):
        key = event.__dict__["key"]
        if key in self.keydown_func_dict:
            self.keydown_func_dict[key](event)

    def key_up(self, event):
        key = event.__dict__["key"]
        if key in self.keyup_func_dict:
            self.keyup_func_dict[key](event)
