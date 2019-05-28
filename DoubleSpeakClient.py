import videoClient
import audioClient
import clientGUI
import netpack
import tkinter as tk

class MediaClient():
    def __init__(self, name):
        self.name = name
        self.__clientNames = {videoClient.ME:name}
        self.__currentFrames = {}
        self.__clientSpeaking = {}

        self.audio = None
        self.video = None

        self.__root = tk.Tk()

    def setAudioServer(self, audioHost, audioPort):
        self.audio = audioClient.AudioClient(audioHost, audioPort, name=name)

    def setVideoServer(self, videoHost, videoPort):
        self.video = videoClient.VideoClient(videoHost, videoPort, name=name)
        
    def startAudio(self):
        return self.audio.start()

    def startVideo(self):
        ret = self.video.start()
        self.__currentFrames = self.video.currentFrames
        return ret

    def startGui(self):
        self.GUI = clientGUI.GUI(self.__root, clientNames=self.__clientNames,
            currentFrames=self.__currentFrames, clientSpeaking=self.__clientSpeaking)

    def startAll(self):
        self.startAudio()
        self.startVideo()
        self.startGui()
        

if __name__ == "__main__":
    name = input("Enter name\n")
    client = MediaClient(name=name)
    client.setAudioServer('127.0.0.1', 8000)
    client.setVideoServer('127.0.0.1', 8100)
    
    while not client.audio.connected:
        client.startAudio()

    while not client.video.connected:
        client.startVideo()

    client.startGui()
