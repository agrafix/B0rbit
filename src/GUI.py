# -*- coding: utf-8 -*-

'''
Created on 04.06.2011

@author: alexander
'''

from tkinter import *
import threading

class OrbitGui:
    
    def __init__(self):
        
        self.closed = False
        
        self.objects = {}
        
        self.scale = 3
                
        master = Tk()
        
        master.title("B0rbit - The ultimate DarkOrbit b0t. Beta v0.1")
        
        master.protocol("WM_DELETE_WINDOW", self._winExitHandler)
        
        self.w = Canvas(master, width=200 * self.scale, height=125 * self.scale)
        self.w.pack()
        
        self.w.create_rectangle(0, 0, 200 * self.scale, 125 * self.scale, fill="black")
        
        self._lineHeroY = self.w.create_line(0 * self.scale, 55 * self.scale, 200 * self.scale, 55 * self.scale, fill="blue")
        self._lineHeroX = self.w.create_line(100 * self.scale, 0 * self.scale, 100 * self.scale, 125 * self.scale, fill="blue")
        
        self._textInfoBox = self.w.create_text(10, 10, anchor=NW, text="Lade...", fill="white")
        
        threading._start_new_thread(mainloop, ())
        
    def SetText(self, strText):
        self.w.itemconfig(self._textInfoBox, text=strText)
      
    def _winExitHandler(self):
        self.closed = True
        
    def _setObj(self, _id, _x, _y, type, color):
        
        id = str(_id) + str(type)
        
        x = int(_x / 100) * self.scale
        y = int(_y / 100) * self.scale
        
        if self.objects.get(id, "d") == "d":
            self.objects[id] = self.w.create_oval(x, y, x+self.scale, y+self.scale, fill=color)
            
        else:
            self.w.coords(self.objects[id], x, y, x+self.scale, y+self.scale)
            
    def _deleteObj(self, _id, type):
        
        id = str(_id) + str(type)
        
        if self.objects.get(id, "d") != "d":
            
            self.w.delete(self.objects[id])
            
            del self.objects[id]
        
    def setShip(self, id, _x, _y):
        
        self._setObj(id, _x, _y, "ship", "white")
            
    def deleteShip(self, id):
        
        self._deleteObj(id, "ship")
        
        
    def setBox(self, id, _x, _y):
        
        self._setObj(id, _x, _y, "box", "yellow")
            
    def deleteBox(self, id):
        
        self._deleteObj(id, "box")
        
    def setOre(self, id, _x, _y):
        
        self._setObj(id, _x, _y, "ore", "green")
            
    def deleteOre(self, id):
        
        self._deleteObj(id, "ore")
    
    def setPlayerPos(self, _x, _y):
        
        x = int(_x / 100) * self.scale
        y = int(_y / 100) * self.scale
        
        self.w.coords(self._lineHeroY, 0, y, 200 * self.scale, y)
        self.w.coords(self._lineHeroX, x, 0, x, 125 * self.scale)
        
    def setDesiredPath(self, centerx, centery, radius):
        
        self.w.create_oval((centerx-radius) * self.scale, (centery-radius) * self.scale, 
                           (centerx+radius) * self.scale, (centery+radius) * self.scale, outline="red")
        
    def setMovingLine(self, _fromX, _fromY, _toX, _toY):
        
        fromX = int(_fromX / 100) * self.scale
        fromY = int(_fromY / 100) * self.scale
        toX = int(_toX / 100) * self.scale
        toY = int(_toY / 100) * self.scale
        
        self.movingLine = self.w.create_line(fromX, fromY, toX, toY, fill="peachpuff")
        
    def killMovingLine(self):
        self.w.delete(self.movingLine)