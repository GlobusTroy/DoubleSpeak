import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from math import sqrt, ceil

WIDTH=1280
HEIGHT=720

root = tk.Tk()
# 640x360 vid

GREY = '#666666'
GREY2 = '#555555'
BLACK = '#000000'
GREEN = '#50eda6'

default_avatar = ImageTk.PhotoImage(image=Image.open("avatar_original.jpg"))
testframe = Image.open("avatar_original.jpg")
vframe = Image.open("Arstotzka_emblem.png")

class GUI:
    def __init__(self, root, clients=[], height=HEIGHT, width=WIDTH):
        self.clients = clients
        self.clientFrames = [None for client in self.clients]
        self.clientSpeaking = [False for client in self.clients]
        self.root = root
        self.root.title('DoubleSpeak')
        style = ttk.Style(root)
        style.theme_use('clam')

        basesizer = tk.Canvas(self.root, height=height, width=width)
        basesizer.pack()

        gold = (1/1.618)
        self.canvas = tk.Canvas(self.root, bg=GREY, bd=5, relief='groove')
        self.canvas.place(relx=0, rely=0, relwidth=gold, relheight=1.0)

        self.frame = tk.Frame(self.root, bd=5, bg=GREY2, relief='groove')
        self.frame.place(relx=gold, rely=0, relwidth=1-gold, relheight=1.0)

        #buttonAdd = tk.Button(self.frame, text='Add')#, #command=self.addClient)
        #buttonAdd.place(relx = 0.1, rely = 0.8, relwidth=0.1618, relheight=0.1)

        buttonAdd = tk.Button(self.frame, text = "Add Client", command= lambda:self.addClient('new'), 
            highlightbackground = GREY2)
        buttonAdd.place(relx = 0.1, rely = 0.9, relwidth=0.25, relheight=0.05)

        buttonRm = tk.Button(self.frame, text = "Remove Client", command= lambda:self.removeClient(self.clients[-1]), 
            highlightbackground = GREY2)
        buttonRm.place(relx = 0.4, rely = 0.9, relwidth=0.25, relheight=0.05)

        self.labels = []
        self.delay = 15
        self.root.update()
        self.update()

        self.root.mainloop()

    def update(self):
        self.canvas.delete('all')

        newLabels = False
        if len(self.labels) != len(self.clients):
            for lbl in self.labels:
                lbl.destroy()
            self.labels = [None for client in self.clients]
            newLabels = True

        for i, client in enumerate(self.clients):
            x,y,w,h = self.getImageDimensions(i, len(self.clients))
            self.clientFrames[i] = ImageTk.PhotoImage(image = testframe.resize( (w,h), Image.ANTIALIAS ))
            self.canvas.create_image(x,y, image=self.clientFrames[i], anchor='nw', tag='vid')

            bd = 2

            if newLabels:
                self.labels[i] = tk.Label(self.canvas, text=self.clients[i],fg='white', bg=GREY2)
                self.labels[i].place(x=x+5*bd, y=y+5*bd, anchor='nw')

            ringColor = BLACK if not self.clientSpeaking[i] else GREEN
            self.canvas.create_rectangle(x+bd//2,y+bd//2, x+w-bd//2, y+h-bd//2, width=bd, outline=ringColor, tag='rect')

        self.root.after(self.delay, self.update)

    def getImageDimensions(self, i, gridSize):
        ratio = 640/360
        bigW = self.canvas.winfo_width()
        bigH = self.canvas.winfo_height()

        ncols = int ( sqrt(gridSize) )
        nrows = ceil (gridSize / ncols)

        maxW = bigW // ncols
        maxH = bigH // nrows

        w = maxW
        h = maxH
        if w / ratio > h:
            w = int(ratio * h)
        else:
            h = int(w / ratio)

        x = (i % ncols) * w
        y = (i//ncols) * h
        return x,y,w,h

    def addClient(self, name):
        self.clients.append(name)
        self.clientFrames.append(None)

        if len(self.clients) == 4 or len(self.clients) == 7:
            self.clientSpeaking.append(True)
        else:
            self.clientSpeaking.append(False)

    def removeClient(self, name):
        idx = self.clients.index(name)
        self.clients.pop(idx)
        self.clientFrames.pop(idx)
        self.clientSpeaking.pop(idx)


GUI(root, clients=['jamie1', 'jamie2'])