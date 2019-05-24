import tkinter as tk
from PIL import ImageTk, Image
from math import sqrt, ceil

WIDTH=1280
HEIGHT=720

root = tk.Tk()
# 640x360 vid

GREY = '#666666'
GREY2 = '#555555'

default_avatar = ImageTk.PhotoImage(image=Image.open("avatar_original.jpg"))
vframe = Image.open("Arstotzka_emblem.png")

class GUI:
    def __init__(self, root, clients=[], height=HEIGHT, width=WIDTH):
        self.clients = clients
        self.clientFrames = [[None, None] for client in self.clients]
        self.root = root
        self.root.title('DoubleSpeak')

        basesizer = tk.Canvas(self.root, height=height, width=width)
        basesizer.pack()

        gold = (1/1.618)
        self.canvas = tk.Canvas(self.root, bg=GREY, bd=5, relief='groove')
        self.canvas.place(relx=0, rely=0, relwidth=gold, relheight=1.0)

        self.frame = tk.Frame(self.root, bd=5, bg=GREY2, relief='groove')
        self.frame.place(relx=gold, rely=0, relwidth=1-gold, relheight=1.0)

        self.delay = 15
        self.root.update()
        self.update()

        self.root.mainloop()

    def update(self):
        for i, client in enumerate(self.clients):
            x,y,w,h = self.getImageDimensions(i, len(self.clients))
            self.clientFrames[i][1] = self.clientFrames[i][0] 
            self.clientFrames[i][0] = ImageTk.PhotoImage(image = vframe.resize( (w,h), Image.ANTIALIAS ))
            self.canvas.create_image(x,y, image=self.clientFrames[i][0], anchor='nw')

        self.root.after(self.delay, self.update)

    def getImageDimensions(self, i, gridSize):
        ratio = 640/360
        maxW = self.canvas.winfo_width()
        maxH = self.canvas.winfo_height()

        nrows = ceil( sqrt(gridSize) )
        w = maxW // nrows
        h = int(w / ratio)
        x = (i % nrows) * w
        y = (i//nrows) * h
        return x,y,w,h


GUI(root, clients=['jamie1', 'jamie2'])