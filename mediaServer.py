from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread, Lock
from queue import Queue
from netpack import Netpack, PackType
from time import time

OK = 'ok'
PINGME = 'pingme'
DEFAULT_BUFFER_SIZE = 4096

class MediaServer:
    SOCKET_TIMEOUT = 0.5
    CLIENT_CONNECTION_TIMEOUT = 5.0
    START_PINGING = 2.0
    MAX_PINGS = 5
    def __init__(self, host, port, bufferSize=DEFAULT_BUFFER_SIZE, tag='media'):
        self.server = socket(family=AF_INET, type=SOCK_DGRAM)
        self.server.settimeout(MediaServer.SOCKET_TIMEOUT)
        self.tag = tag

        self.hostAddr = (host,port)
        self.bufferSize = bufferSize

        self.clients = {}
        self.clientCharId = {}
        self.timeOfLastMessage = {}
        self.missedPings = {}

        self.activeThread = None

    def start(self):
        self.server.bind(self.hostAddr)
        print('Server bound to {}'.format(self.hostAddr))
        
        print('Starting listening thread...')
        self.activeThread = Thread(target=self.receiveData)
        self.activeThread.start()

    def receiveData(self):
        while True:
            try:
                data, addr = self.server.recvfrom(self.bufferSize)
                datapack = Netpack(datapacket=data)
                self.handlePacket(datapack, addr)
            except timeout:
                pass
            self.checkConnections()

    def handlePacket(self, datapack, addr):
        if self.clients.get(addr, None) is None:
            try:
                if datapack.PackType != PackType.Handshake:
                    return

                name = datapack.data.decode(encoding='UTF-8')

                self.clients[addr] = name
                self.clientCharId[addr] = len(self.clients)
                self.timeOfLastMessage[addr] = time()
                self.missedPings[addr] = 0

                print('{} has connected to {} on {}!'.format(name, self.tag, addr))
                datapack = Netpack(packType=PackType.Handshake, data=OK.encode(encoding='UTF-8'))
                self.server.sendto(datapack.out(), addr)
            except:
                pass
            return

        self.timeOfLastMessage[addr] = time()
        if datapack.PackType == PackType.ClientData:
            self.broadcastData(addr, datapack)
        elif datapack.PackType == PackType.KeepAlive:
            self.missedPings[addr] = 0
            if datapack.data.decode() == PINGME:
                pingpack = Netpack(packType=PackType.KeepAlive, data=OK.encode(encoding='UTF-8'))
                self.server.sendto(pingpack.out(), addr)
        elif datapack.PackType == PackType.NameQuery:
            char = int(datapack.data.decode(encoding='UTF-8'))
            addrQuery = {v:k for k,v in self.clientCharId.items()}[char]
            namepack = Netpack(packType=PackType.NameQuery, 
                data=(str(char)+':'+self.clients[addrQuery]).encode(encoding='UTF-8'))
            self.server.sendto(namepack.out(), addr)


    def checkConnections(self):
        currTime = time()
        disconnected = []
        
        for addr, lastTime in self.timeOfLastMessage.items():
            if currTime - lastTime > MediaServer.CLIENT_CONNECTION_TIMEOUT:
                disconnected.append(addr)
                
            elif ((currTime - lastTime >= MediaServer.START_PINGING) and 
            self.missedPings[addr] < MediaServer.MAX_PINGS):
                datapack = Netpack(packType=PackType.KeepAlive, data=PINGME.encode(encoding='UTF-8'))
                self.server.sendto(datapack.out(), addr)
                self.missedPings[addr] += 1

        for addr in disconnected:
            self.disconnectClient(addr)

    def disconnectClient(self, addr):
        name = self.clients[addr]
        print('{} has disconnected from {}!'.format(name, self.tag))

        del self.clients[addr]
        del self.clientCharId[addr]
        del self.timeOfLastMessage[addr]
        del self.missedPings[addr] 



    def broadcastData(self, sentFrom, datapack):
        datapack.head = self.clientCharId[sentFrom]
        for client in self.clients:
            if client != sentFrom:
                self.server.sendto(datapack.out(), client)


#AUDIO_PORT = 4000

#HOST = input("Enter Server IP\n")
#PORT = int(input("Enter Port Number\n"))

#server = MediaServer(HOST, PORT)
if __name__ == "__main__":
    server = MediaServer('127.0.0.1', 8000)
    server.start()