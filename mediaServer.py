from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread, Lock
from queue import Queue
from netpack import Netpack, PackType
from time import time

OK = 'ok'

DEFAULT_BUFFER_SIZE = 2049

class MediaServer:
    SOCKET_TIMEOUT = 0.5
    CLIENT_CONNECTION_TIMEOUT = 5.0
    START_PINGING = 2.0
    MAX_PINGS = 3
    def __init__(self, host, port, bufferSize=DEFAULT_BUFFER_SIZE):
        self.server = socket(family=AF_INET, type=SOCK_DGRAM)
        self.server.settimeout(MediaServer.SOCKET_TIMEOUT)

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

                print('{} has connected on {}!'.format(name, addr))
                datapack = Netpack(packType=PackType.Handshake, data=OK.encode(encoding='UTF-8'))
                self.server.sendto(datapack.out(), addr)
            except:
                pass
            return

        self.timeOfLastMessage[addr] = time()
        if datapack.PackType == PackType.ClientData:
            self.broadcastAudio(addr, datapack.data)
        elif datapack.PackType == PackType.KeepAlive:
            self.missedPings[addr] = 0

    def checkConnections(self):
        currTime = time()
        disconnected = []
        
        for addr, lastTime in self.timeOfLastMessage.items():
            if currTime - lastTime > MediaServer.CLIENT_CONNECTION_TIMEOUT:
                disconnected.append(addr)
                
            elif ((currTime - lastTime >= MediaServer.START_PINGING) and 
            self.missedPings[addr] < MediaServer.MAX_PINGS):
                datapack = Netpack(packType=PackType.KeepAlive, data=OK.encode(encoding='UTF-8'))
                self.server.sendto(datapack.out(), addr)
                #print('Pinging {}...'.format(self.clients[addr]))
                self.missedPings[addr] += 1

        for addr in disconnected:
            self.disconnectClient(addr)

    def disconnectClient(self, addr):
        name = self.clients[addr]
        print('{} has disconnected!'.format(name))

        del self.clients[addr]
        del self.clientCharId[addr]
        del self.timeOfLastMessage[addr]
        del self.missedPings[addr] 



    def broadcastAudio(self, sentFrom, data):
        datapack = Netpack(head=self.clientCharId[sentFrom], data=data)
        for client in self.clients:
            if client != sentFrom:
                self.server.sendto(datapack.out(), client)


#AUDIO_PORT = 4000

#HOST = input("Enter Server IP\n")
#PORT = int(input("Enter Port Number\n"))

#server = MediaServer(HOST, PORT)

server = MediaServer('127.0.0.1', 8000)
server.start()