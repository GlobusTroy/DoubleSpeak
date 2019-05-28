from mediaServer import MediaServer

if __name__ == "__main__":
    audioServer = MediaServer('127.0.0.1', 8000, tag='audio')
    audioServer.start()

    videoServer = MediaServer('127.0.0.1', 8100, tag='video')
    videoServer.start()