#!/usr/bin/env python

"""Spyse fire fighter scenario demo"""

from random import randint

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour
from spyse.core.platform.platform import Platform
from spyse.core.semant.semant import Semant
from spyse.core.semant.environment import PlaneEnvironment
from spyse.app.app import App

import wx
from spyse.core.agents.wxagent import wxAgent

class DummyBehaviour(TickerBehaviour):
    def on_tick(self):
        self.period = randint(3, 10)
        print self.agent.name, "count:", self.tick_count

class DummyAgent(Agent):
    def setup(self):
        print "DummyAgent.setup"
        self.add_behaviour(DummyBehaviour())

class GrowBehaviour(Behaviour):
    def setup(self, env):
        pass

class Fire(Semant):
    def setup(self, env, place_args):
        self.env = env
        self.env.place(self.name, place_args[0], place_args[1], place_args[2], place_args[3], place_args[4], place_args[5], place_args[6])
        #name, type, spot=[0.0, 0.0, 0.0], form='box', size=[1, 1, 1], velo=[0.0, 0.0, 0.0], view=(10, 90), cond=None
        self.add_behaviour(GrowBehaviour(env=self.env))

class SetFireBehaviour(Behaviour):
    def setup(self, env):
        pass

class Pyromaniac(Semant):
    def setup(self, env, place_args):
        self.env = env
        self.env.place(self.name, place_args[0], place_args[1], place_args[2], place_args[3], place_args[4], place_args[5], place_args[6])
        #name, type, spot=[0.0, 0.0, 0.0], form='box', size=[1, 1, 1], velo=[0.0, 0.0, 0.0], view=(10, 90), cond=None
        self.add_behaviour(SetFireBehaviour(env=self.env))

class SearchFireBehaviour(Behaviour):
    def setup(self, env):
        self.env = env
        self.max_speed = 10

    def action(self):
        agent_name = self.agent.name
        e = self.env.read(agent_name)

        rx = e.x + randint(-self.max_speed, self.max_speed)
        ry = e.y + randint(-self.max_speed, self.max_speed)
        self.env.move(agent_name, x=rx, y=ry)
        #self.env.turn(agent, 180)

class ExtinguishBehaviour(Behaviour):
    def setup(self, env):
        pass

class FireTruck(Semant):
    def setup(self, env, place_args):
        self.env = env
        self.env.place(self.name, place_args[0], place_args[1], place_args[2], place_args[3], place_args[4], place_args[5], place_args[6])
        #name, type, spot=[0.0, 0.0, 0.0], form='box', size=[1, 1, 1], velo=[0.0, 0.0, 0.0], view=(10, 90), cond=None
        self.add_behaviour(SearchFireBehaviour(env=self.env))
        self.add_behaviour(ExtinguishBehaviour(env=self.env))

class DrawEnvironmentBehaviour(Behaviour):
    def setup(self, view):
        self.view = view
        self.objects = {}
        #self.counter = 0
        self.dc = None

    def action(self):
        if not self.dc:
            self.dc = wx.ClientDC(self.agent.frame.context)
        pen = wx.Pen('white')
        self.dc.SetPen(pen)
        self.dc.DrawRectangle(0, 0, 800, 800)
        #pen.SetColour('blue')
        #self.dc.SetPen(pen)
        #self.dc.DrawCircle(10 + self.counter, 10 + self.counter, 5)
        #self.counter = self.counter + 5

        entities = self.view.entities()
        #print "entities", entities

        for e in entities:
#            #print datetime.today(), e.name, e.type
            if e.type == 'Fire':
                self.drawFire(e)
            elif e.type == 'FireTruck':
                self.drawFireTruck(e)

    def drawFire(self, e):
        pass

    def drawFireTruck(self, e):
        pen = wx.Pen('blue')
        self.dc.SetPen(pen)
        self.dc.DrawCircle(e.x, e.y, 5)

class wxViewerAgent(wxAgent):
    """View agent"""

    def setup(self, view, size):
        super(wxViewerAgent, self).setup(size)
        self.__view = view
        self.__datastore = {}
        self.add_behaviour(DrawEnvironmentBehaviour(view=self.__view))
        self.frame.Closed = self.Closed
        
    def Closed(self):
        Platform.shutdown()

    def create_widgets(self, frame):
        #wx.Frame.__init__(self, parent, 2400, "I've been driving in my car, it's not quite a Jaguar", size=(800,600) )
        outerbox = wx.BoxSizer(wx.VERTICAL)
        glbox = wx.BoxSizer(wx.VERTICAL)
        outerbox.Add(glbox, 5, wx.EXPAND)
        tID = wx.NewId()
        self.frame = frame

        frame.context = wx.Panel(frame)  # SimulationContext(frame)
        glbox.Add(frame.context, 1, wx.EXPAND)

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        outerbox.Add( buttonbox, 0, wx.FIXED_MINSIZE)
        buttonbox.Add(wx.Button(frame, 1003, "Reset View"), 0)
#        wx.EVT_BUTTON(frame, 1003, frame.context.OnButtonResetView)
        buttonbox.Add(wx.Button(frame, 1004, "Add Car"), 0)
#        wx.EVT_BUTTON(frame, 1004, frame.context.OnButtonNewCar)
        buttonbox.Add(wx.Button(frame, 1005, "Full Screen"), 0)
#        wx.EVT_BUTTON(frame, 1005, frame.context.OnFullScreenToggle)
#        frame.context.addEventHandler( 'keypress', name = 'f', function = frame.context.OnFullScreenToggle)
#        frame.context.addEventHandler( 'keyboard', name = '<escape>', function = frame.context.OnFullScreenToggle)
        frame.SetAutoLayout(True)
        frame.SetSizer( outerbox )

#class FireFighters(SpyseApp):
#    def process():
#        print "FireFighters spyseApp"
#        self.start_agent(DummyAgent, 'Agent007')

class MyApp(App):
    def run(self, args):
        e = PlaneEnvironment()
        ce = e.controller
        #
        #ff = FireFighters()
        #self.start_agent(...)
        #
        self.start_agent(Pyromaniac, 'Pyro',
            env=ce,
            place_args=[ 'Pyromaniac', [8.0, -4.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        self.start_agent(Fire, 'Fire_00',
            env=ce,
            place_args=[ 'Fire', [8.0, -4.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        self.start_agent(Fire, 'Fire_01',
            env=ce,
            place_args=[ 'Fire', [8.0, -4.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        self.start_agent(FireTruck, 'Truck_00',
            env=ce,
            place_args=[ 'FireTruck', [200.0, 100.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        self.start_agent(FireTruck, 'Truck_01',
            env=ce,
            place_args=[ 'FireTruck', [400.0, 100.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        # ve
        ve = e.view
        self.start_agent(wxViewerAgent, 'EnvironmentViewer', view=ve, size=(800, 800))
        wxAgent.run_GUI()
        

if __name__ == "__main__":
    MyApp()

