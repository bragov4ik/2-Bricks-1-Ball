from library.constants import WELCOME_MESSAGE
from aiOpponent.botSettings import SERVER_IP, SERVER_PORT
from typing import Dict, Tuple
import socket
import json
import pygame.time

class Bot:
    connection: socket.socket
    clock: pygame.time.Clock
    player_location: int
    ball_location: Tuple[float, float]

    def __init__(self):
        self.connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        self.connection.bind((SERVER_IP, SERVER_PORT))
        self.server_connect(SERVER_IP, SERVER_PORT)
        self.clock = pygame.time.Clock()
    
    def run(self):
        while True:
            # Recieve and read message
            data, address = self.connection.recvfrom(1024)
            state: Dict[str, Dict] = json.loads(data)
            ball = state['Ball']
            ball_pos = ball['Position']
            # Construct input
            new_y = ball_pos[1]
            message_dict = {
                'PlayerInput': {
                    'Position': new_y
                }
            }
            message_bytes = json.dumps(message_dict)
            # Send
            self.connection.sendto(message_bytes, (SERVER_IP, SERVER_PORT))
    
    def server_connect(self, serverIP, serverPort) -> bool:
        """
        Uses socket inside the class.  Lets the server know that this
        client wants to play the game
        Returns if the operation is successful.
        """
        # Maybe later create a proper 3-way handshake
        self.connection.sendto(
            WELCOME_MESSAGE,
            (serverIP, serverIP)
        )
        
        
