#!/usr/bin/env python

""" Environment Demo
    
    The environment demo shows how to use the distributed
    environment model.
    
    The following arguments can be given to the program:
    arg0: If 1 -> Create a Viewer else -> nothing
    arg1: The number of cars to create
    arg2-5: Create an environment segment with bounds xMin=arg2, xMax=arg3, yMin=arg4, yMax=arg5
    args6: Color of the cars
    
    Usage examples:
     
    Local:
    Make every Spyse instance be aware of every change in the environment.
        envdemo.py --port=9001 --distribution=broadcast-retrieve --env=local 1 5
        envdemo.py --port=9002 --distribution=broadcast-retrieve --env=local 0 5     
     
    Central:
    Store the environment at a central place.
    server, no view, 0 cars: 
        envdemo.py --threading=normal --port=9001 --distribution=server --env=server 0 0
    client, no view, 5 cars: 
        envdemo.py --threading=normal --port=9002 --distribution=client --env=client 0 5
    client, view, 0 cars:
        envdemo.py --threading=normal --port=9003 --distribution=client --env=client 1 0
         
    Segmented:
    Divide the environment among multiple Spyse instances
    Box1 xMin:   0 xMax: 150 yMin:   0 yMax: 150 Blue Cars
        envdemo.py --port=9001 --ns=start --env=dist 1 5   0 150   0 150 blue
    Box2 xMin: 150 xMax: 300 yMin:   0 yMax: 150 Red Cars
        envdemo.py --port=9002 --ns=local --env=dist 1 5 150 300   0 150 red
    Box3 xMin:   0 xMax: 150 yMin: 150 yMax: 300 Yellow Cars
        envdemo.py --port=9003 --ns=local --env=dist 1 5   0 150 150 300 yellow
    Box4 xMin: 150 xMax: 300 yMin: 150 yMax: 300 Green Cars
        envdemo.py --port=9004 --ns=local --env=dist 1 5 150 300 150 300 green

    N.B. This demo seems to work properly on Windows, but not on GNU/Linux.
"""
__version__ = '1.0'

from spyse.app.app import App
from spyse.core.semant.environment import PlaneEnvironment, DistEnvironment, DistController, Entity

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.platform.platform import Platform
from random import randint

from spyse.core.agents.wxagent import wxAgent
from spyse.util import vector
import wx
import threading
import random
import time

class Car(Agent):
    """ Represents a random moving Car """
    def setup(self, env, location, color):
        self.color = color
        self.env = env
        self.env.place(self.name, 'Car', spot=location)
        self.env.set_color(self.name, self.color)
        self.add_behaviour(CarBehaviour(env=self.env))

class CarBehaviour(Behaviour):
    """ A car will choose a random location on the map, move towards it
        and choose a new destination when it has reached his current one """
    def setup(self, env):
        self.env = env
        self.dest= None
        self.route = 0
        
    def get_destination(self):
        while True:
            destx = random.randint(0,300)
            desty = random.randint(0,300)
            dest = vector.Vector([destx,desty,0])
            
            # check if the destination lies within the model of the segmented environment
            # if the environment is segmented
            if isinstance(self.env, DistController):
                if self.env.in_model(dest):
                    return dest
            else:
                return dest
            
        
    def get_destination2(self):
        """ Move in a square pattern """
        if(self.route == 0):
            self.route = 1
            return vector.Vector([225,50,0])
        elif(self.route == 1):
            self.route = 2
            return vector.Vector([225,225,0])
        elif(self.route == 2):
            self.route = 3
            return vector.Vector([50,225,0])
        elif(self.route == 3):
            self.route = 0
            return vector.Vector([50,50,0])
        
    def action(self):
        if self.dest is None: # choose a destination if one isn't present
            self.dest = self.get_destination()
            
        s = self.env.read(self.agent.name)    # get current position
        if s is None:        # if this fails, sleep for a while and retry later
            self.sleep(0.5)
            return
        
        dx = self.dest.x - s.x        # calculate the X distance we have to travel
        if dx > 5:                    # move to the destination in small steps
            dx = random.randint(1,5)
        elif dx < -5:
            dx = random.randint(-5,-1)
            
        dy = self.dest.y - s.y        # calculate the Y distance we have to travel
        if dy > 5:                    # move to the destination in small steps
            dy = random.randint(1,5)
        elif dy < -5:
            dy = random.randint(-5,-1)
            
        x = s.x+dx    # calculate new x
        y = s.y+dy    # and y position
        
        if dx == 0 and dy == 0:    # if we are at our destination, pick a new one
            self.dest = self.get_destination()

        self.env.move(self.agent.name, x=x, y=y)    # move the agent
        self.sleep(0.15)    # sleep

#---------------------------------------------------------------------------------

class DrawEnvironmentBehaviour(Behaviour):
    """ Draws the moving cars """
    def setup(self, view, size):
        self.view = view
        self.size = size
        self.dc = None

    def action(self):
        if not self.dc:
            self.dc = wx.ClientDC(self.agent.frame.window)
        bmp = wx.Image('spyse/demo/distenv/envdemo-back.bmp', wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        
        pen = wx.Pen('white')
        brush = wx.Brush('white')
        self.dc.SetPen(pen)
        self.dc.SetBrush(brush)
        self.dc.DrawRectangle(0, 0, self.size[0], self.size[1])
        self.dc.DrawBitmap(bmp,-self.agent.offset[0],-self.agent.offset[1])

        entities = self.view.entities()
        for e in entities:
            self.dc.SetBrush(brush)
            if isinstance(e, Entity) and e.type == 'Car':
                self.drawCar(e)
        self.sleep(0.15)

    def drawCar(self, e):
        pen = wx.Pen(e.color)
        pen.SetWidth(3)
        self.dc.SetPen(pen)
        self.dc.DrawCircle(e.x-self.agent.offset[0], e.y-self.agent.offset[1], 5)
           
class ViewerAgent(wxAgent):
    """ViewerAgent will draw the cars, if the environment is segmented
        the offset will be the upperleft coordinate for the box which 
        will be drawn by this agent. """
    def setup(self, view, size, offset):
        super(ViewerAgent, self).setup((size[0]+8, size[1]+27))
        self.__view = view
        self.__size = size
        self.offset = offset
        self.add_behaviour(DrawEnvironmentBehaviour(view=self.__view, size=self.__size))
        self.frame.SetPosition((self.offset[0],self.offset[1]))
        self.frame.closed = self.closed
        
    def closed(self):
        Platform.shutdown()
        


#---------------------------------------------------------------------------------

# Application

class MyApp(App):
    def run(self, args):
        width=500
        height=500
        offset=(0,0)

        if len(args) > 5:    # segmented environment
            x_mina=int(args[2])
            x_maxa=int(args[3])
            y_mina=int(args[4])
            y_maxa=int(args[5])
            offset = (x_mina,y_mina)
            e = DistEnvironment(x_min=x_mina, x_max=x_maxa, y_min=y_mina, y_max=y_maxa)
            width = x_maxa-x_mina
            height = y_maxa-y_mina
            carloc = [x_mina+(x_maxa-x_mina)/2,y_mina+(y_maxa-y_mina)/2, 0]
        else:    # Plane Environment
            e = PlaneEnvironment(x_min=0, x_max=width, y_min=0, y_max=height)
            carloc = [300,300,0]
        ec = e.controller
        ev = e.view
        
        car_color='red'
        if len(args) > 6:
            car_color = args[6]

        if len(args) >0 and args[0] == '1':
            self.start_agent(ViewerAgent, 'Viewer', view=ev, size=[width, height], offset=offset)

        if len(args) >1:
            amount = int(args[1])
            for i in range(amount):
                self.start_agent(Car, 'Car-'+str(random.randint(0, 1000000)), env=ec, location=carloc, color=car_color)                

        wxAgent.run_GUI()


if __name__ == "__main__":
    MyApp()
