#!/usr/bin/env python

from spyse.app.app import App
from spyse.core.semant.environment import PlaneEnvironment

from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour
from random import randint

from spyse.core.agents.wxagent import wxAgent
import wx

# Car agent:
class Car(Agent):
    def setup(self, env, location):
        self.env = env
        self.env.place(self.name, 'Car', spot=location)
        self.add_behaviour(CarBehaviour(env=self.env))

class CarBehaviour(Behaviour):
    def setup(self, env):
        self.env = env

    def action(self):
        s = self.env.read(self.agent.name)
        dx = randint(-5,5)
        dy = randint(-5,5)
        x = s.x+dx
        y = s.y+dy
        self.env.move(self.agent.name, x=x, y=y)
        self.sleep(0.2)

#---------------------------------------------------------------------------------

# Viewer Agent
class DrawEnvironmentBehaviour(Behaviour):
    def setup(self, view, size):
        self.view = view
        self.size = size
        self.dc = None

    def action(self):
        if not self.dc:
            self.dc = wx.ClientDC(self.agent.frame.window)
        pen = wx.Pen('white')
        self.dc.SetPen(pen)
        self.dc.DrawRectangle(0, 0, self.size[0], self.size[1])

        entities = self.view.entities()
        for e in entities:
            if e.type == 'Car':
                self.drawCar(e)
        self.sleep(0.1)

    def drawCar(self, e):
        pen = wx.Pen('red')
        pen.SetWidth(3)
        self.dc.SetPen(pen)
        self.dc.DrawCircle(e.x, e.y, 5)
           
class ViewerAgent(wxAgent):
    """View agent"""
    def setup(self, view, size):
        super(ViewerAgent, self).setup((size[0]+8, size[1]+27))
        self.__view = view
        self.__size = size
        self.add_behaviour(DrawEnvironmentBehaviour(view=self.__view, size=self.__size))
        self.frame.closed = self.closed
        
    def closed(self):
        Platform.shutdown()

#---------------------------------------------------------------------------------

# Application

class MyApp(App):
    def run(self, args):
        width = 500
        height = 500
        e = PlaneEnvironment(x_min=0, x_max=width, y_min=0, y_max=height)
        ec = e.controller
        ev = e.view
        self.start_agent(Car, 'Car1', env=ec, location=[300, 300, 0])
        self.start_agent(Car, 'Car2', env=ec, location=[200, 200, 0])
        self.start_agent(ViewerAgent, 'Viewer', view=ev, size=[width, height])
        wxAgent.run_GUI()

if __name__ == "__main__":
    MyApp()
