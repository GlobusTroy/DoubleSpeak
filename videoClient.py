import cv2
import numpy as np

class VideoCamera(object):
    def __init__(self):
        # OpenCV to capture from device 0.
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def getFrame(self, resolution=360):
        success, image = self.video.read()

        #Calculate new image shape
        shapeOrig = image.shape
        ratio = resolution / shapeOrig[0]
        shapeOut = ( int(shapeOrig[1] * ratio), resolution )

        #Resize the image
        image = cv2.resize(image, shapeOut ,interpolation=cv2.INTER_AREA)

        # Encode raw image into jpg
        ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tobytes()

from socket import socket, AF_INET, SOCK_DGRAM, timeout
from threading import Thread
from netpack import Netpack, Videopack, PackType
from time import time, sleep
from math import ceil

OK = 'ok'
PINGME = 'pingme'
DEFAULT_BUFFER_SIZE = 4096
CLIENT_CONNECTION_TIMEOUT = 7.5
START_PINGING = 4.5
OLD_PACKET_THRESHOLD = 2.0
ME = -1

class VideoClient:
    def __init__(self, serverHost, serverPort, bufferSize=DEFAULT_BUFFER_SIZE, 
    name='client', fps=60):
        self.name = name
        self.server = (serverHost, serverPort)
        self.client = socket(family=AF_INET, type=SOCK_DGRAM)
        self.client.settimeout(CLIENT_CONNECTION_TIMEOUT)
        self.bufferSize = bufferSize

        self.cam = VideoCamera()
        self.currentFrames = {}
        self.chunkedFrames = {}

        self.lastReceived = time()
        self.lastSent = time()
        self.connected = False
        self.fps = fps

        self.imageId = 0
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
        return self.connected

    def sendFrameChunks(self, imageBytes):
        chunkSize = self.bufferSize - 4
        numChunks = ceil(len(imageBytes) / chunkSize)
        for i in range(numChunks):
            dataChunk = imageBytes[:chunkSize]
            imageBytes = imageBytes[chunkSize:]
            nextPacket = Videopack(packType=PackType.ClientData, data=dataChunk,
                imageId=self.imageId, index=i, imageLen=numChunks)
            self.client.sendto(nextPacket.out(), self.server)
        self.imageId = (self.imageId + 1) % 256

    def processFrameChunk(self, datapack):
        clientId = datapack.head

        newFrame = (self.chunkedFrames[clientId].get(datapack.imageId, None) is None)
        oldFrame = (not newFrame) and (time() - self.chunkedFrames[clientId][datapack.imageId].get('last', time()) 
            > OLD_PACKET_THRESHOLD)

        #New frame to construct
        if newFrame or oldFrame:
            self.chunkedFrames[clientId][datapack.imageId] = {}

        if datapack.index == 0:
            self.chunkedFrames[clientId][datapack.imageId]['len'] = datapack.imageLen

        #Add chunk to proper frame list
        self.chunkedFrames[clientId][datapack.imageId][datapack.index] = datapack.data
        #Update last packet received timestamp
        self.chunkedFrames[clientId][datapack.imageId]['last'] = time()
        #print('Grabbed frame #{}'.format(datapack.index))

        #Check if Frame construction is complete
        imageLen = self.chunkedFrames[clientId][datapack.imageId].get('len', float('inf'))
        #currLen = number of chunks = len(dict) -1 for 'last' and -1 for potentially 'len'
        currLen = len(self.chunkedFrames[clientId][datapack.imageId]) - 1
        if imageLen != float('inf'):
            currLen -= 1

        #print('{}/{} chunks gathered for image {}'.format(currLen,imageLen,datapack.imageId))
        if currLen >= imageLen:
            #print('constructing...')
            if self.isLater(datapack.imageId, self.chunkedFrames[clientId]['currId']):
                image = self.constructFrame( self.chunkedFrames[clientId][datapack.imageId] )
                self.currentFrames[clientId] = image
                #print('VideoClient: Currframes = {}'.format(len(self.currentFrames)))
                self.chunkedFrames[clientId]['currId'] = datapack.imageId
            del self.chunkedFrames[clientId][datapack.imageId]

    def isLater(self, id1, id2):
        if id1 == id2:
            return True
        if id1 < id2:
            id1 += 256
        if id1 > id2 and id1 < id2 + 128:
            return True
        else:
            return False

    def constructFrame(self, chunkDict):
        chunkList = [chunkDict[i] for i in range(chunkDict['len'])]
        byteString = b''.join(chunkList)
        image = cv2.imdecode(np.fromstring(byteString, np.uint8), cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def sendVideo(self):
        while self.connected:
            if time() - self.lastReceived >= START_PINGING:
                pingpack = Netpack(packType=PackType.KeepAlive, data=PINGME.encode('UTF-8'))
                self.client.sendto(pingpack.out(), self.server)
            if (time() - self.lastSent) > (1 / self.fps):
                frameBytes = self.cam.getFrame()
                self.currentFrames[ME] = cv2.imdecode(np.fromstring(frameBytes, np.uint8), cv2.IMREAD_COLOR)
                self.currentFrames[ME] = cv2.cvtColor(self.currentFrames[ME], cv2.COLOR_BGR2RGB)
                self.sendFrameChunks(frameBytes)
                self.lastSent = time()

    def recieveVideo(self):
        while self.connected:
            try:
                data, addr = self.client.recvfrom(self.bufferSize)
                datapack = Netpack(datapacket=data)
                self.lastReceived = time()

                if datapack.PackType == PackType.ClientData:
                    datapack = Videopack(datapacket=data)
                    if self.chunkedFrames.get(datapack.head, None) is None:
                        self.chunkedFrames[datapack.head] = {'currId':0}
                    self.processFrameChunk(datapack)

                elif datapack.PackType == PackType.KeepAlive and datapack.data.decode() == PINGME:
                    outpack = Netpack(packType=PackType.KeepAlive, data=OK.encode('UTF-8'))
                    self.client.sendto(outpack.out(), self.server)

            except timeout:
                self.connected = False
                print('Lost connection to server!')
    
def printImg(videoClient):
    while videoClient.connected:
        for client, frame in videoClient.currentFrames.items():
            print('Client {} | Len: {}'.format(client, len(frame)))
            cv2.imshow('Client #{}'.format(client), frame)
            cv2.waitKey( 1000 / fps )

if __name__ == "__main__":
    name = input("Enter name\n")
    client = VideoClient('127.0.0.1', 8000, name=name)
    client.start()

    sleep(5)
    printImg(client)

    client.receiveThread.join()
    client.sendThread.join()
    displayThread.join()

#HOST = input("Enter Server IP\n")
#PORT = int(input("Enter Port Number\n"))
#name = input("Enter name\n")

#client.start()

#client.receiveThread.join()
#client.sendThread.join()
    