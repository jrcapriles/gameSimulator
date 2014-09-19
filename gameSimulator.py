# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 19:27:57 2014

@author: joser
"""


import pygame, ode, random, Buttons
from math import atan2, acos, asin, sin, cos
import matplotlib.pyplot as plt

from pygame.locals import *
from numpy import *
from Point import *
from Buttons import *


class gameSimulator( object ):

    def __init__( self, *args, **kwargs):
       # Initialize pygame
        pygame.init()
        self.width = kwargs.get('width',600)
        self.height = kwargs.get('height',400)
        self.length = kwargs.get('length',200)        
        self.fps = kwargs.get('fps',50)
        self.G = kwargs.get('gravity',-9.81)
        self.world = ode.World()
        self.world.setGravity((0,self.G,0))
        
        self.createScreen()
        self.createButtons()
        
        #Variables of this game
        self.FIRE = False
        self.ANGLE = 0.25
        self.POWER = 6.5
        self.dt = 1.0/self.fps
        
        self.buffer = []
        self.bufferHead = 0
        self.bufferTail = 0
        self.bufferIsEmpty = True
        self.bufferSize = 100
        
        self.correctX = 0
        self.correctY = 0
        
        self.initBuffer()
        
    def initBuffer(self):
        for i in range(0,self.bufferSize):
            self.buffer.append((0,0))

    def createScreen(self):
        # Open a display
        self.srf = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Game Simulator")
        
        #Parameters
        self.dt = 1.0/self.fps
        self.loopFlag = True
                
 
    def createButtons(self):      
        #Buttons
        self.goal_button = Buttons.Button(self.srf, color = (200,0,0), x = 10, y = 10, length =  50, height = 25, width = 0, text = "Button_1", text_color = (255,255,255), font_size = 20, fade_on = False)
        self.switch_button = Buttons.Button(self.srf, color = (200,0,0), x = 60, y = 10, length =  50, height = 25, width = 0, text = "Button_2", text_color = (255,255,255), font_size = 20, fade_on = False)
        self.follow_button = Buttons.Button(self.srf, color = (200,0,0), x = 110, y = 10, length =  50, height = 25, width = 0, text = "Button_3", text_color = (255,255,255), font_size = 20, fade_on = False)
        self.noise_button = Buttons.Button(self.srf, color = (200,0,0), x = 160, y = 10, length =  50, height = 25, width = 0, text = "Button_4", text_color = (255,255,255), font_size = 20, fade_on = False)
        
        #Button Dictionary
        self.buttons = {0 : self.goal_button,
                        1 : self.switch_button,
                        2 : self.follow_button,
                        3 : self.noise_button}


    def loadBackground(self,filename):
        self.backgroundImage = pygame.image.load(filename).convert()
        self.backgroundRect = self.backgroundImage.get_rect()
    
    def loadImage(self, filename):
        image = pygame.image.load(filename)
        return image

    def world2screen(self, x, y):
        return int(self.width/2 + 128*x), int(self.length/2 - 128*y)
    
    def screen2world(self, x, y):
        return (float(x - self.width/2)/128), (float(-y + self.length/2)/128)


    def checkEvents(self):
        events = pygame.event.get()
        for e in events:
            if e.type==QUIT:
                pygame.quit()
            elif e.type==KEYDOWN:
                if e.key == K_f:
                    print "FIRE!!!"
                    self.FIRE = True
                    self.Vox = self.POWER * cos(self.ANGLE)
                    self.Voy = self.POWER * sin(self.ANGLE)
                elif e.key == K_UP:
                    self.ANGLE = self.ANGLE + 0.1
                    print self.POWER, self.ANGLE
                elif e.key == K_DOWN:
                    self.ANGLE = self.ANGLE - 0.1
                    print self.POWER, self.ANGLE
                elif e.key == K_LEFT:
                    self.POWER = self.POWER - 0.1
                    print self.POWER, self.ANGLE
                elif e.key == K_RIGHT:
                    self.POWER = self.POWER + 0.1
                    print self.POWER, self.ANGLE
                else:
                    pygame.quit()
    
    
    def updateBackground(self, color = None):
        if color is not None:
            self.srf.fill(color)
        else:
            self.srf.blit(self.backgroundImage,self.backgroundRect)

    def updateImage(self,image, position):
        self.srf.blit(image,position)
        self.addBuffer(position)

    def getBuffer(self):
        return zip(*self.buffer)

    def addBuffer(self,newValue):
        self.buffer[self.bufferHead] = newValue 
        if self.bufferHead == self.bufferSize-1:
            self.bufferHead = 0
            self.bufferTail = 0
        else: 
            if self.bufferHead == self.bufferTail and not self.bufferIsEmpty:
                self.bufferHead = self.bufferHead +1
                self.bufferTail = self.bufferHead
            else:
                self.bufferHead = self.bufferHead +1
            
        self.bufferIsEmpty = False



    def updateTrace(self,x,y,color):
        for i in range(0,self.bufferSize):
            self.srf.set_at((x[i]+self.correctX,y[i]+self.correctY),color)
            

    def run(self):
        
        # Simulation loop.
        self.clk = pygame.time.Clock()
        
        self.loadBackground("images/screen.png")
        gun = self.loadImage("images/gun.jpg")
        gunPos = [50,320]
        bullet = self.loadImage("images/bullet.jpg")
        self.correctX, self.correctY = bullet.get_rect().size
        self.correctX = self.correctX/2
        self.correctY = self.correctY/2
        
        x,y = self.screen2world(230,320)
        
        while True:
            # Check for events
            self.checkEvents()
                
            self.updateBackground()
            self.updateImage(gun,gunPos)
            
            if self.FIRE:
                self.Voy = self.Voy + self.G* self.dt
                x = x + self.Vox*self.dt
                y = y + self.Voy*self.dt + 0.5*self.G*self.dt**2
                self.updateImage(bullet, self.world2screen(x,y))
            else:
                if self.bufferIsEmpty is False:
                    plotx, ploty = self.getBuffer()
                    self.updateTrace(plotx, ploty,(255,255,255))
                    
                
            if self.FIRE and (y < -2.5 or y >2.5 or x >2.5 or x<-2.5):
                self.FIRE = False
                x,y = self.screen2world(230,320)
                plotx, ploty = self.getBuffer()
                
            
            pygame.display.flip()

            # Next simulation step
            self.world.step(self.dt)

            # Try to keep the specified framerate    
            self.clk.tick(self.fps)

    