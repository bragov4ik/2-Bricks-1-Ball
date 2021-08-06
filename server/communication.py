from typing import Dict, List, Tuple
import socket
import json

from library.constants import WELCOME_MESSAGE
from server.serverSettings import BIND_IP, BIND_PORT

class Communication:
    """
    Keeps up-to-date buffered information recieved from clients (with 
    `startUpdating`) and gives simpler interface for addressing them
    (indexes instead of addresses).
    """
    player_addrs: Tuple[Tuple[str, int]]
    player_data: List[Dict]
    players_num: int
    connection_socket: socket.socket
    

    def __init__(self, players_num):
        """
        Wait for required number of clients and creates necessary
        entries for them.
        """
        self.player_addrs = ()
        self.player_data = []
        self.players_num = players_num
        self.connection_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        self.connection_socket.bind(
            (BIND_IP, BIND_PORT)
        )
        self.connect_clients()
    

    def connect_clients(self):
        players = []
        for i in range(self.players_num):
            msg = ''
            while msg != WELCOME_MESSAGE:
                msg, addr = self.connection_socket.recvfrom(1024)
            # msg == WELCOME_MESSAGE
            players.append(addr)
            self.player_data.append({})
    

    def sendToPlayer(self, msg, player_index) -> int:
        """
        Calls `sendto` with corresponding player's address.  Passes the
        value recieved (view `sendto` docs for details).
        """
        return self.connection_socket.sendto(
            msg,
            self.player_addrs[player_index]
        )

    
    def start_updating(self):
        """
        Continuously updates any recieved player information.  Blocks,
        so it makes sense to put it in different thread.
        """
        while True:
            msg, index = self.recv_from_any()
            self.save_player_data(index, msg)

    
    def get_player_info(self, player_index) -> Dict:
        """
        Get the latest recieved information from given player.
        """
        return self.player_data[player_index]

    
    def recv_from_any(self) -> Tuple[bytes, int]:
        """
        Recieves message and gives it with the index of sending player.
        """
        while True:
            msg, addr = self.connection_socket.recvfrom(1024)
            try:
                index = self.player_addrs.index(addr)
            except ValueError:
                print("Recieved message from unexpected address '{}'!".format(addr))
                continue
            # Index was found, return the message
            return (msg, index)


    def save_player_data(
        self,
        player_index: int,
        player_data: bytes
    ) -> None:
        data_loaded = json.loads(player_data)
        self.player_data[player_index] = data_loaded
