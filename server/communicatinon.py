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
    playerAddrs: Tuple[Tuple[str, int]]
    playerData: List[Dict]
    playersNum: int
    connectionSocket: socket.socket
    

    def __init__(self, playersNum):
        """
        Wait for required number of clients and creates necessary
        entries for them.
        """
        self.playerAddrs = ()
        self.playerData = []
        self.playersNum = playersNum
        self.connectionSocket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        self.connectionSocket.bind(
            (BIND_IP, BIND_PORT)
        )
        self.connectClients()
    

    def connectClients(self):
        players = []
        for i in range(self.playersNum):
            msg = ''
            while msg != WELCOME_MESSAGE:
                msg, addr = self.connectionSocket.recvfrom(1024)
            # msg == WELCOME_MESSAGE
            players.append(addr)
            self.playerData.append({})
    

    def sendToPlayer(self, msg, playerIndex) -> int:
        """
        Calls `sendto` with corresponding player's address.  Passes the
        value recieved (view `sendto` docs for details).
        """
        return self.connectionSocket.sendto(
            msg,
            self.playerAddrs[playerIndex]
        )

    
    def startUpdating(self):
        """
        Continuously updates any recieved player information.  Blocks,
        so it makes sense to put it in different thread.
        """
        while True:
            msg, index = self.recvFromAny()
            self.savePlayerData(index, msg)

    
    def getPlayerInfo(self, playerIndex) -> Dict:
        """
        Get the latest recieved information from given player.
        """
        return self.playerData[playerIndex]

    
    def recvFromAny(self) -> Tuple[bytes, int]:
        """
        Recieves message and gives it with the index of sending player.
        """
        while True:
            msg, addr = self.connectionSocket.recvfrom(1024)
            try:
                index = self.playerAddrs.index(addr)
            except ValueError:
                print("Recieved message from unexpected address '{}'!".format(addr))
                continue
            # Index was found, return the message
            return (msg, index)


    def savePlayerData(
        self,
        playerIndex: int,
        playerData: bytes
    ) -> None:
        dataLoaded = json.loads(playerData)
        self.playerData[playerIndex] = dataLoaded
