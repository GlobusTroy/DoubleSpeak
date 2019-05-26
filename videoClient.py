import cv2

class VideoCamera(object):
    def __init__(self):
        # OpenCV to capture from device 0.
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def getFrame(self):
        success, image = self.video.read()

        # Encode raw image into jpg
        return image
        ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tobytes()


from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread
from netpack import Netpack, PackType
from time import time, sleep

OK = 'ok'
DEFAULT_BUFFER_SIZE = 2049
CLIENT_CONNECTION_TIMEOUT = 7.5

class VideoClient:
    def __init__(self, serverHost, serverPort, bufferSize=DEFAULT_BUFFER_SIZE, 
    name='client', fps=60):
        self.name = name
        self.server = (serverHost, serverPort)
        self.client = socket(family=AF_INET, type=SOCK_DGRAM)
        self.client.settimeout(CLIENT_CONNECTION_TIMEOUT)
        self.bufferSize = bufferSize

        self.cam = VideoCamera()
        self.clientFrames = {}

        self.lastReceived = time()
        self.connected = False
        self.fps = fps

        self.sendThread = None
        self.receiveThread = None

    def connectToServer(self):
        if self.connected:
            return True

        datapack = Netpack(packType=PackType.Handshake, data=self.name.encode(encoding='UTF-8'))
        self.client.sendto(datapack.out(), self.server)

        data, addr = self.client.recvfrom(self.bufferSize)
        datapack = Netpack(datapacket=data)

        if (addr==self.server and datapack.PackType==PackType.Handshake and 
        datapack.data.decode('UTF-8')==OK):
            print('Connected to server successfully!')
            self.connected = True
        return self.connected

    def start(self):
        self.connectToServer()
        if self.connected:
            self.receiveThread = Thread(target=self.recieveVideo)
            self.receiveThread.start()

            self.sendThread = Thread(target=self.sendVideo)
            self.sendThread.start()

    #def sendFrameChunks(self, image):


    def sendVideo(self):
        while self.connected:
            data = self.cam.getFrame()
            datapack = Netpack(packType=PackType.ClientData, data=data)
            cv2.imshow('frame', data)
            self.client.sendto(datapack.out(), self.server)
            
            sleep( 1/self.fps )

    def recieveVideo(self):
        while self.connected:
            try:
                data, addr = self.client.recvfrom(self.bufferSize)
                datapack = Netpack(datapacket=data)

                if datapack.PackType == PackType.ClientData:
                    self.clientFrames[datapack.head] = datapack.data
                    #cv2.imshow('frame', datapack.data)

                elif datapack.PackType == PackType.KeepAlive:
                    outpack = Netpack(packType=PackType.KeepAlive, data=OK.encode('UTF-8'))
                    self.client.sendto(outpack.out(), self.server)

            except timeout:
                self.connected = False
                print('Lost connection to server!')
    


#HOST = input("Enter Server IP\n")
#PORT = int(input("Enter Port Number\n"))
#name = input("Enter name\n")

#client = AudioClient(HOST, PORT, name=name)
#client = VideoClient('127.0.0.1', 8000, name=name)
#client.start()

#client.receiveThread.join()
#client.sendThread.join()
    