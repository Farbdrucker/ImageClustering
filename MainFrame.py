# Main Frame
from Tkinter import *
from PIL import Image
import ImageTk
import tkMessageBox
import Tkinter, Tkconstants, tkFileDialog
import numpy as np
import os
from AdaptiveCrossApproximation import ACA
from ConvSplitting import ConvSplittingFunc

class MainFrame(object):
    canvas_width = 300
    canvas_height = 400
    defaultBrushSize = 5
    maxBrushSize = 50
    DEFAULT_COLOR = 'blue'


    oImage = None
    mask = 0
    Marker = np.zeros((canvas_height, canvas_width))
    activeMarker = False
    k = 10

    rootDir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, root):

        self.root = root
        self.Canvas = Canvas(self.root,
           width = self.canvas_width,
           height = self.canvas_height,
           bg='white')
        self.Canvas.grid(column = 0, rowspan = 10)
        self.LoadButton = Button(self.root, text = 'load', command = self.LoadImage)
        self.LoadButton.grid(column = 1, row = 0)

        #self.brush_button = Button(self.root, text='brush', command=self.use_brush)
        #self.brush_button.grid(column = 1, row = 1)

        self.createMask = Button(self.root, text = 'mask', command= self.CalcMask)
        self.createMask.grid(column = 1, row =4)

        self.supervisedButton = Button(self.root,
                                        text = 'supervise',
                                        command = self.ConvSplit)
        self.supervisedButton.grid(column = 1, row =6)

        self.InvertMask = Button(self.root, text = 'invert mask', command = self.Invert)
        self.InvertMask.grid(column = 1, row = 5)

        self.SaveButton = Button(self.root, text = 'save', command = self.Save)
        self.SaveButton.grid(column = 1, row = 8)
        self.PaintSetup()

    def Save(self):
        saveDir = tkFileDialog.asksaveasfilename(initialdir = self.rootDir,
                                        title = "Select file",
                                        filetypes = (("postscript files","*.ps"),
                                                    ("all files","*.*")))
        retval = self.Canvas.postscript(file = saveDir)

    def PaintSetup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.defaultBrushSize
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        #self.active_button = self.brush_button
        self.Canvas.bind('<B1-Motion>', self.paintA)
        self.Canvas.bind('<B3-Motion>', self.paintB)
        self.Canvas.bind('<ButtonRelease-1>', self.reset)
        self.Canvas.bind('<ButtonRelease-3>', self.reset)
        self.Canvas.bind_all("<Button-4>", self.__OnMouseWheel)
        self.Canvas.bind_all("<Button-5>", self.__OnMouseWheel)

    def __OnMouseWheel(self, event):
        if event.num == 4 and self.defaultBrushSize <= self.maxBrushSize:
            self.defaultBrushSize += 5
        if event.num == 5 and self.defaultBrushSize > 0:
            self.defaultBrushSize -= 5
        print self.defaultBrushSize

    def ResetMarker(self):
        self.activeMarker = False
        self.Marker = np.zeros((self.canvas_height, self.canvas_width))

    def Invert(self):
        if self.V is not None:
            self.V *=-1
            self.CalcMask(new = 0)
        else:
            tkMessageBox.showinfo("Error", "There is nothing to invert")

    def LoadImage(self):
        # load the .gif image file
        filename = tkFileDialog.askopenfilename(initialdir = self.rootDir,
                                        title = "Select file",
                                        filetypes = (("jpeg files","*.jpg"),
                                                    ("all files","*.*")))
        print filename
        if filename != '':
            self.oImage = Image.open(filename)
            self.canvas_width, self.canvas_height= self.GetNewSize(self.oImage)

            self.oImage = self.oImage.resize((self.canvas_width, self.canvas_height))

            self.IntoCanvas(self.oImage)
            # new image -> cleaer calculated eigenvectors
            self.V = None
            self.createMask.config(text = 'mask')
            self.ResetMarker()

    def GetNewSize(self, Im):
        width, height = Im.size
        totalNum = self.canvas_width * self.canvas_height
        ratio = float(width)/height

        newWidth = int(np.sqrt(totalNum * ratio))
        newHeight = int(np.sqrt(totalNum * 1./ratio))
        return newWidth, newHeight

    def IntoCanvas(self, image):
        self.image = ImageTk.PhotoImage(image)
        self.Canvas.config(width = self.canvas_width, height = self.canvas_height)
        self.Canvas.create_image(0, 0, image=self.image, anchor=NW)

    def paintA(self,event):
        self.paint(event, 'blue')
    def paintB(self,event):
        self.paint(event, 'green')

    def paint(self, event, color):
        self.activeMarker = True
        self.line_width = self.defaultBrushSize
        if self.old_x and self.old_y:
            self.Canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
            if event.x >= 0 and event.y >= 0 and event.x< self.canvas_width and event.y < self.canvas_height:
                if color == 'blue':
                    self.Marker[event.y][event.x] = 1
                elif color =='green':
                    self.Marker[event.y][event.x] = -1

        self.old_x = event.x
        self.old_y = event.y


    def reset(self, event):
        self.old_x, self.old_y = None, None

    def CalcMask(self, new = 1):
        if self.V is not None:
            if self.mask> self.k-1:
                self.mask = 0
            self.ApplyMask(np.array(self.oImage), self.V[self.mask][0])
            self.UpdateButtonName()
            self.ResetMarker()
            self.mask += new

        elif self.oImage is not None:
            self.mask = self.k -2
            self.GetEig()
            self.ApplyMask(np.array(self.oImage),self.V[self.mask][0])
            self.UpdateButtonName()
            print 'finished'
        else:
            tkMessageBox.showinfo("Error", "Load Image first!")

    def GetEig(self):
        self.D,self.V = ACA(image = np.array(self.oImage),
                            maxRank = 2+ self.k,
                            k = self.k).GetEig()
        return self.D, self.V

    def UpdateButtonName(self):
        self.createMask.config(text = 'mask ' + str(self.mask+1) + '/' + str(self.k))


    def ApplyMask(self, A , u):
        print u.shape
        u = np.squeeze(np.asarray(u))
        m = np.max(np.abs(u))
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                #tmp = (u[i * A.shape[1] + j]/m + 2) *255
                #A[i][j][:] = tmp
                if u[i * A.shape[1] + j] <0:
                    if len(A.shape) == 2:
                        A[i][j] = 255
                    if len(A.shape) == 3:
                        A[i][j][0] = 255
                        A[i][j][1] = 0
                        A[i][j][2] = 0


        Im = Image.fromarray(np.uint8(A))
        self.IntoCanvas(Im)

    def ConvSplit(self):
        if self.oImage is not None and self.activeMarker == True:
            if self.V is None:
                self.GetEig()
            u0 = np.mat(self.Marker).flatten().T
            u0,u = ConvSplittingFunc(u0 =u0, phi = self.V, lamb = self.D, maxIter = 100)
            print u0
            self.ApplyMask(np.array(self.oImage),u0)
        else:
            tkMessageBox.showinfo("Error", "An error occured, load image and tag an object!")
