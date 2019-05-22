from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread, Lock
from queue import Queue
from netpack import Netpack, PackType

OK = 'ok'

DEFAULT_BUFFER_SIZE = 2049

class AudioServer:
    def __init__(self, host, port, bufferSize=DEFAULT_BUFFER_SIZE):
        self.server = socket(family=AF_INET, type=SOCK_DGRAM)
        self.hostAddr = (host,port)
        self.clients = {}
        self.clientCharId = {}
        self.bufferSize = bufferSize

        self.activeThread = None

    def start(self):
        self.server.bind(self.hostAddr)
        print('Server bound to {}'.format(self.hostAddr))
        
        print('Starting listening thread...')
        self.activeThread = Thread(target=self.receiveAndBroadcastAudio)
        self.activeThread.start()

    def receiveAndBroadcastAudio(self):
        while True:
            data, addr = self.server.recvfrom(self.bufferSize)

            if self.clients.get(addr, None) is None:
                try:
                    name = data.decode(encoding='UTF-8')
                    self.clients[addr] = name
                    self.clientCharId[addr] = len(self.clients)

                    print('{} has connected on {}!'.format(name, addr))
                    self.server.sendto(OK.encode(encoding='UTF-8'), addr)
                except:
                    pass
                continue

            datapack = Netpack(datapacket=data)
            if datapack.PackType == PackType.ClientData:
                self.broadcastAudio(addr, datapack.data)

    def broadcastAudio(self, sentFrom, data):
        datapack = Netpack(head=self.clientCharId[sentFrom], data=data)
        for client in self.clients:
            if client != sentFrom:
                self.server.sendto(datapack.out(), client)


#AUDIO_PORT = 4000

#HOST = input("Enter Server IP\n")
#PORT = int(input("Enter Port Number\n"))

#server = AudioServer(HOST, PORT)

server = AudioServer('127.0.0.1', 8000)
server.start()