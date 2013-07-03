#!/usr/bin/env python

"""Spyse traffic jam demo for semant"""

# add state to cars, such that they can detect when a light turns green, enlarge view, start them all together
# brake depending on distance from obstacle
# fix bug with hanging cars at end of lane
# use ZODB for environment, Zemantic
# use separate behaviours
# use 3APL for behaviours

from spyse.core.agents.agent import Agent
from spyse.core.agents.wxagent import wxAgent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour
from spyse.core.semant.semant import Semant
from spyse.core.semant.environment import PlaneEnvironment
from spyse.util import vector
from spyse.app.app import App

import math

from datetime import datetime

import wx

try:
    from wx import glcanvas
    haveGLCanvas = True
except ImportError:
    haveGLCanvas = False

try:
    # The Python OpenGL package can be found at
    # http://PyOpenGL.sourceforge.net/
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    haveOpenGL = True
except ImportError:
    haveOpenGL = False

from OpenGLContext import wxinteractivecontext
from OpenGLContext.scenegraph import basenodes, imagetexture
from OpenGLContext.events.timer import Timer

#from wx.lib.floatcanvas.FloatCanvas import FloatCanvas

from math import sin, cos, pi

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

__scenario = {}

class ScenarioHandler(ContentHandler):
    inside_tag = 0
    data = ""

    def startDocument(self):
            print "<html>"

    def endDocument(self):
            print "</html>"

    def startElement(self, el, attr):
        print "startElement"
        print el
        print attr

        if el == "pythonbooks":
            print "<table border='1'>"
            print "<tr>"
            print "<th>Author(s)</th><th>Title</th><th>Publisher</th>"
            print "</tr>"
        elif el == "book": 
            self.book = {}
        elif el in ["author","publisher","title"]:
            self.inside_tag = 1

    def endElement(self, el):
        if el == "pythonbooks":
            print "</table>"
        elif el == "book":
            print "<tr>"
            print "<td>%s</td><td>%s</td><td>%s</td>" % \
                (self.book['author'], 
                self.book['title'], 
                self.book['publisher'])
            print "</tr>"
        elif el in ["author","publisher","title"]:
            self.book[el] = self.data
            self.data = ''
            self.inside_tag = 0

    def characters(self, chars):
        if self.inside_tag:
            self.data+=chars


class Event(object):
    __time = 0
    __target = None
    __operation = None


class ScenarioDriver(Agent):
    def setup(self):
        """Read and parse scenario from an XML file."""

        # Content handler
        h = ScenarioHandler()

        # Instantiate parser
        parser = make_parser()

        # Register content handler
        parser.setContentHandler(h)

        # Parse XML file
        fp = open('pythonbooks.xml','r')
        parser.parse(fp)

    def action(self):
        """Run the scenario by firing events at the appropriate time."""

class Car(Semant):
    def setup(self, env, place_args):
        self.env = env
        self.env.place(self.name, place_args[0], place_args[1], place_args[2], place_args[3], place_args[4], place_args[5], place_args[6])
        #name, type, spot=[0.0, 0.0, 0.0], form='box', size=[1, 1, 1], velo=[0.0, 0.0, 0.0], view=(10, 90), cond=None
        self.add_behaviour(MoveBehaviour(env=self.env))

# TODO: ReadContextBehaviour
class ReadContextBehaviour(TickerBehaviour):    # ==> Semant, also move neighbours/inview/etc to Semant
    def action(self):
        agent_name = self.agent.name
        e = self.env.read(agent_name)
        #self.agent.context = self.env.neighbours(agent_name, 20)
        # ==> datastore

class AvoidCarsBehaviour(Behaviour):
    def setup(self, env):
        self.env = env
        self.max_speed = 1.5

    def action(self):
        agent_name = self.agent.name
        e = self.env.read(agent_name)

        if (e.x > 49) or (e.x < -49):
            self.env.move(agent_name, x=e.x+sign(e.x), y=-e.y)
            self.env.turn(agent_name, 180)

        nbs = self.env.inview(agent_name)
        if len(nbs) > 0:
            #n = self.env.read(nbs[0])
            print datetime.today(), agent_name, 'sees', nbs
            for nb in nbs:
                n = self.env.read(nb)
                if n.type == 'TrafficLight':
                    if n.cond == 'red':
                        self.env.slower(agent_name, 0.3)
                    else:
                        self.env.speed(agent_name, min(e.v + 0.1, self.max_speed))
                    break
                elif n.type == 'Car':
                    self.env.slower(agent_name, 0.15)
            #self.env.right(agent_name)
        else:
            self.env.speed(agent_name, min(e.v + 0.02, self.max_speed))

        self.env.forward(agent_name)

class ObeyRedLightBehaviour(Behaviour):
    def setup(self, env):
        self.env = env
        self.max_speed = 1.5

    def action(self):
        agent_name = self.agent.name
        e = self.env.read(agent_name)

        if (e.x > 49) or (e.x < -49):
            self.env.move(agent_name, y=-e.y)
            self.env.turn(agent_name, 180)

        nbs = self.env.inview(agent_name)
        if len(nbs) > 0:
            #n = self.env.read(nbs[0])
            print datetime.today(), agent_name, 'sees', nbs
            for nb in nbs:
                n = self.env.read(nb)
                if n.type == 'TrafficLight':
                    if n.cond == 'red':
                        self.env.slower(agent_name, 0.3)
                    else:
                        self.env.speed(agent_name, min(e.v + 0.1, self.max_speed))
                    break
                elif n.type == 'Car':
                    self.env.slower(agent_name, 0.15)
            #self.env.right(agent_name)
        else:
            self.env.speed(agent_name, min(e.v + 0.02, self.max_speed))

        self.env.forward(agent_name)

class MoveBehaviour(Behaviour):
    def setup(self, env):
        self.env = env
        self.max_speed = 1.5

    def action(self):
        agent_name = self.agent.name
        e = self.env.read(agent_name)

        if (e.x > 49) or (e.x < -49):
            if e.x > 0:
                sign = 1
            else:
                sign = -1
        if (e.x > 49) or (e.x < -49):
            self.env.move(agent_name, x=e.x-sign, y=-e.y)
            self.env.turn(agent_name, 180)

        nbs = self.env.inview(agent_name)
        if len(nbs) > 0:
            #n = self.env.read(nbs[0])
            print datetime.today(), agent_name, 'sees', nbs
            for nb in nbs:
                n = self.env.read(nb)
                if n.type == 'TrafficLight':
                    if n.cond == 'red':
                        self.env.slower(agent_name, 0.3)
                    else:
                        self.env.speed(agent_name, min(e.v + 0.1, self.max_speed))
                    break
                elif n.type == 'Car':
                    self.env.slower(agent_name, 0.15)
            #self.env.right(agent_name)
        else:
            self.env.speed(agent_name, min(e.v + 0.02, self.max_speed))

        self.env.forward(agent_name)

class TrafficLight(Semant):
    def setup(self, env, place_args):
        self.env = env
        self.env.place(self.name, place_args[0], place_args[1], place_args[2], place_args[3], place_args[4], place_args[5], place_args[6])
        #name, type, spot=[0.0, 0.0, 0.0], form='box', size=[1, 1, 1], velo=[0.0, 0.0, 0.0], view=(10, 90), cond=None
        self.add_behaviour(LightBehaviour(period=10))

class LightBehaviour(TickerBehaviour):
    def on_tick(self):
        agent_name = self.agent.name
        e = self.agent.env.read(agent_name)
        if e.cond == 'green':
            e.cond = 'red'
        else:
            e.cond = 'green'
        print 'Light turns', e.cond
        self.agent.env.write(agent_name, e)

class DummyBehaviour(Behaviour):
    def setup(self):
        self.i = 0
    def action(self):
        self.i += 1

class wxViewerAgent(wxAgent):
    """View Agent"""

    def setup(self, view, size):
        super(wxViewerAgent, self).setup(size)
        self.__view = view
        self.__datastore = {}
        self.add_behaviour(DrawEnvironmentBehaviour(view=self.__view))

    def create_widgets(self, frame):
        #wx.Frame.__init__(self, parent, 2400, "I've been driving in my car, it's not quite a Jaguar", size=(800,600) )
        outerbox = wx.BoxSizer(wx.VERTICAL)
        glbox = wx.BoxSizer(wx.VERTICAL)
        outerbox.Add(glbox, 5, wx.EXPAND)
        tID = wx.NewId()
        self.frame = frame
        self.frame.context = SimulationContext(frame)
        glbox.Add(frame.context, 1, wx.EXPAND)

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        outerbox.Add( buttonbox, 0, wx.FIXED_MINSIZE)
        buttonbox.Add(wx.Button(frame, 1003, "Reset View"), 0)
        wx.EVT_BUTTON(frame, 1003, frame.context.OnButtonResetView)
        buttonbox.Add(wx.Button(frame, 1004, "Add Car"), 0)
        wx.EVT_BUTTON(frame, 1004, frame.context.OnButtonNewCar)
        buttonbox.Add(wx.Button(frame, 1005, "Full Screen"), 0)
        wx.EVT_BUTTON(frame, 1005, frame.context.OnFullScreenToggle)
        frame.context.addEventHandler( 'keypress', name = 'f', function = frame.context.OnFullScreenToggle)
        frame.context.addEventHandler( 'keyboard', name = '<escape>', function = frame.context.OnFullScreenToggle)
        frame.SetAutoLayout(True)
        frame.SetSizer( outerbox )

class DrawEnvironmentBehaviour(Behaviour):
    def setup(self, view):
        self.view = view
        self.objects = {}

    def action(self):
        entities = self.view.entities()

#        remove deleted entities from view

        for e in entities:
            #print datetime.today(), e.name, e.type
            if e.type == 'Agent':
                self.drawAgent(e)
            elif e.type == 'Car':
                self.drawCar(e)
            elif e.type == 'TrafficLight':
                self.drawTrafficLight(e)
            elif e.type == 'Road':
                self.drawRoad(e)

    def drawAgent(self, e):
        # uses Tkinter
        self.canvas = self.agent.canvas    # pass as args to setup()
        self.zoom = self.agent.zoom    # pass as args to setup()

        agent = self.canvas.find_withtag(e.name)
        #print 'drawAgent'
        if agent is ():
            #print 'create'
            h = (360-e.h)%360
            self.canvas.create_oval(self.zoom*(e.x-20), self.zoom*(e.y-20), self.zoom*(e.x+20), self.zoom*(e.y+20), width=1, tags=e.name)
            self.canvas.create_arc(self.zoom*(e.x-20), self.zoom*(e.y-20), self.zoom*(e.x+20), self.zoom*(e.y+20), start=(h-45)%360, extent=90, width=3, tags=e.name)    # stipple on arcs does not work on Windows !!!
            #self.canvas.create_oval(self.zoom*(e.x-20), self.zoom*(e.y-20), self.zoom*(e.x+20), self.zoom*(e.y+20), fill="#226699", stipple="gray25", width=0, tags=e.name)    # stipple on ovals does not work on Windows !!!
            #self.canvas.create_arc(self.zoom*(e.x-20), self.zoom*(e.y-20), self.zoom*(e.x+20), self.zoom*(e.y+20), start=e.h-45, extent=90, fill="#3377AA", stipple="gray50", width=1, tags=e.name)    # stipple on arcs does not work on Windows !!!
            self.canvas.create_rectangle(self.zoom*(e.x-1), self.zoom*(e.y-1), self.zoom*(e.x+1), self.zoom*(e.y+1), fill="#FF7733", width=0, tags=e.name)
            self.objects[e.name] = (e.x, e.y, e.h)
        else:
            #print 'move'
            self.canvas.create_line(self.zoom*e.x, self.zoom*e.y, self.zoom*(e.x + e.v*cos(e.h/180.0*pi)), self.zoom*(e.y + e.v*sin(e.h/180.0*pi)), tags='trace')
            d = self.objects[e.name]
            dx = d[0]
            dy = d[1]
            dh = d[2]
            if dh != e.h:
                agent = self.canvas.find_withtag(e.name)
                for a in agent:
                    if self.canvas.type(a) == 'arc':
                        h = (360-e.h)%360
                        self.canvas.itemconfigure(a, start=(h-45)%360)
            self.objects[e.name] = (e.x, e.y, e.h)
            self.canvas.move(e.name, self.zoom*(e.x-dx), self.zoom*(e.y-dy))

#            ac = self.canvas.coords(e.name)
#            print ac
#            x = e.x
#            y = e.y
#            w = ac[2] - ac[0]
#            h = ac[3] - ac[1]
#            print x, y, w, h
#            self.canvas.coords(e.name, x, y, x+w, y+h)

    def drawCar(self, e):
        # uses pyOpenGLContext

        car = self.agent.context.getScene().getDEF(e.name)
        if car is None:
            self.agent.context.addCar(e)
        else:
            # update existing car
            #t = car.translation
            #car.translation = (t[0] + e.velo.x, t[1] + e.velo.y, t[2] + e.velo.z)
            car.translation = e.spot

            #r = car.rotation
            car.rotation = (0.0, 0.0, 1.0, e.face.phi)
            #print 'car.rotation', car.rotation

    def drawTrafficLight(self, e):
        # uses pyOpenGLContext

        light = self.agent.frame.context.getScene().getDEF(e.name)
        if light is None:
            self.agent.frame.context.addTrafficLight(e)
        else:
            # update existing light
            if e.cond == 'red':
                light.children[1].children[0].appearance.material.diffuseColor=(1.0, 0.0, 0.0)
                light.children[1].children[0].appearance.material.emissiveColor=(1.0, 0.0, 0.0)
            elif e.cond == 'green':
                light.children[1].children[0].appearance.material.diffuseColor=(0.0, 1.0, 0.0)
                light.children[1].children[0].appearance.material.emissiveColor=(0.0, 1.0, 0.0)
            else:
                light.children[1].children[0].appearance.material.diffuseColor=(0.0, 0.0, 1.0)
                light.children[1].children[0].appearance.material.emissiveColor=(0.0, 0.0, 1.0)

    def drawRoad(self, e):
        # uses pyOpenGLContext
        pass

class SimulationContext(wxinteractivecontext.wxInteractiveContext):
    riding = True
    counter = 0
    cars = 0
    initialPosition = (0, 0, 90)
    initialOrientation = (0, 1, 0, 0)

    def getScene(self):
        return self.sg

    def OnInit(self):
        # draw the ground surface
        self.cars = 0
        self.returnValues = None     # for FullScreen
        self.sg = basenodes.sceneGraph(
            children = [
                basenodes.Transform(
                    translation = (0, 0, -1),
                    children = [
                        # Ground
                        basenodes.Shape(
                            geometry = basenodes.Box(
                                size = (100, 100, 1),
                            ),
                            appearance=basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.3, 0.3, 0.15),
                                    transparency = 0.0,
                                ),
                                #texture = imagetexture.ImageTexture(url = ["traffic.png"]),
                            ),
                        ),
                        # Road 1
                        basenodes.Transform(
                            translation = (0, -2.5, 0),
                            children = [
                                basenodes.Shape(
                                    geometry = basenodes.Box(
                                        size = (100, 2, 1.5),
                                    ),
                                    appearance=basenodes.Appearance(
                                        material = basenodes.Material(
                                            diffuseColor = (0.6, 0.6, 0.3),
                                            transparency = 0.0,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        # Road 2
                        basenodes.Transform(
                            translation = (0, 2.5, 0),
                            children = [
                                basenodes.Shape(
                                    geometry = basenodes.Box(
                                        size = (100, 2, 1.5),
                                    ),
                                    appearance=basenodes.Appearance(
                                        material = basenodes.Material(
                                            diffuseColor = (0.6, 0.6, 0.3),
                                            transparency = 0.0,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                # Light
                basenodes.PointLight(
                    location=(-25, -25, 25),
                ),
                basenodes.DirectionalLight(
                    ambientIntensity = 2.5,
                    intensity = 1.5,
                    color = (1, 1, 1),
                    direction = (1, 1, -1),
                ),
            ],
        )
        self.sg.regDefName('Ground', self.sg.children[0])
        self.sg.getDEF('Ground').translation = (0.0, 0.0, -1.0)

        self.addTunnel()
#        self.addTrafficLight()
#        self.addCar()

        self.time = Timer(duration = 32.0, repeating = 1)
        self.time.addEventHandler("fraction", self.OnTimerFraction)
        self.time.register(self)
        self.time.start()

        self.rotation =  0.0

    def addCar(self, e):
        car = basenodes.Transform(
            children = [
                # Car Body
                basenodes.Transform(
                    translation = (-e.size.x/2, -e.size.y/2, -e.size.z/2),
                        children = [
                            basenodes.Shape(
                                geometry = basenodes.Box(
                                    size = e.size,
                                ),
                                appearance = basenodes.Appearance(
                                    material = basenodes.Material(
                                        diffuseColor = (0.5, 0.0 ,0.5),
                                        transparency = 0.0,
                                ),
                            ),
                        ),
                    ],
                ),
                # Neighbours
                basenodes.Transform(
                    translation = (-e.size.x/2, -e.size.y/2, -e.size.z/2),
                    children = [
                        basenodes.Shape(
                            geometry = basenodes.Sphere(
                                radius = e.d,
                                slices=24, stacks=24,
                            ),
                            appearance=basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.75, 1.0 ,0.75),
                                    transparency = 0.9,
                                ),
                            ),
                        ),
                    ],
                ),
                # View
                basenodes.Transform(
                    translation = (-e.size.x/2+e.d/2 * math.cos(e.a/2 *(math.pi/180)), -e.size.y/2, -e.size.z/2),
                    rotation = (0.0, 0.0, 1.0, 90/180.0*pi),
                    children = [
                        basenodes.Shape(
                            geometry = basenodes.Cone(
                                bottomRadius = e.d * math.sin(e.a/2 *(math.pi/180)),
                                height = e.d * math.cos(e.a/2 *(math.pi/180)),
                                bottom = False,
                                side = True,
                                slices=24, stacks=24,
                            ),
                            appearance=basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.5, 1.0, 0.5),
                                    transparency = 0.75,
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )
        self.sg.children.append(car)
        self.sg.regDefName(e.name, car)
        car.translation = (e.x, e.y, e.z)
        #car.rotation = ()
        #self.cars = self.cars + 1

    def addTrafficLight(self, e):
        # Traffic Light
        traffic = basenodes.Transform(
            children = [
                # Foot
                basenodes.Transform(
                    translation = (e.x, e.y, e.z+1.5),
                    rotation = (1.0, 0.0, 0.0, 90/180.0*pi),
                    children = [
                        basenodes.Shape(
                            geometry = basenodes.Cylinder(
                                height = 3.5,
                                radius = 0.2,
                                side = True,
                                top = False,
                                bottom = False,
                            ),
                            appearance = basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.5, 0.5, 0.5),
                                    transparency = 0.0,
                                ),
                            ),
                        ),
                    ],
                ),
                # Head
                basenodes.Transform(
                    translation = (e.x, e.y, e.z+4.0),
                    children = [
                        basenodes.Shape(
                            geometry = basenodes.Sphere(
                                radius = 0.75,
                            ),
                            appearance = basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.0, 1.0, 0.0),
                                    emissiveColor = (0.0, 1.0, 0.0),
                                    ambientIntensity = 0.5,
                                    transparency = 0.25,
                                ),
                            ),
                        ),
                    ],
                ),
                # Light
#                basenodes.Transform(
#                    children = [
#                        basenodes.SpotLight(
#                            location= (8, -3, 4),
#                            intensity = 1.0,
#                            direction = (-1, -1, -1),
#                            color = (0, 1, 0),
#                            on = True,
#                        ),
#                        basenodes.PointLight(
#                            location= (8, -3, 4),
#                            intensity = 1.0,
#                            color = (0, 1, 0),
#                            on = True,
#                            radius = 15
#                        ),
#                    ],
#                ),
            ],
        )
        self.sg.children.append(traffic)
        self.sg.regDefName(e.name, traffic)
        #print traffic.children[1].center
        #print traffic.children[1].translation

    def addTunnel(self):
        tunnel = basenodes.Transform(
            children = [
                basenodes.Transform(
                    translation = (30.0, 0.0, 2.0),
                    rotation = (0.0, 0.0, 1.0, 90/180.0*pi),
                    children = [
                        basenodes.Shape(
                            geometry = basenodes.Cylinder(
                                height = 30.0,
                                radius = 6.0,
                                side = True,
                                top = False,
                                bottom = False,
                                slices=24, stacks=24,
                            ),
                            appearance = basenodes.Appearance(
                                material = basenodes.Material(
                                    diffuseColor = (0.5, 0.5, 0.5),
                                    transparency = 0.2,
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )
        self.sg.children.append(tunnel)
        self.sg.regDefName('Tunnel', tunnel)

    def getSceneGraph( self ):
        """Get the scene graph for the context (or None)"""
        return self.sg

    def OnTimerFraction( self, event ):
        pass

#from Nehe8
#    BLENDSTYLES = [
#        (),
#        (GL_SRC_ALPHA, GL_ONE), # what the demo uses originally
#        (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA), # this is what should be used with sorted triangles
#        (GL_SRC_ALPHA, GL_DST_ALPHA), # just for kicks...

#        glEnable(GL_BLEND)
#        glDisable(GL_DEPTH_TEST)
#        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glDepthMask( 0 ) # prevent updates to the depth buffer...

#        """Update our rotation from the timer event"""
#        self.counter = self.counter + 1
#        for c in range(self.cars):
#            car = self.sg.getDEF('Car'+str(c))
#            x = car.translation[0]
#            #print 'Car'+str(c), x
#            car.translation = (x + 0.05, 0.0, 0.0)

    def OnButtonResetView( self, event ):
        """Handle the wxPython event from our button"""
        vp = self.platform
        vp.setPosition((0.0, 0.0, 90.0, 1.0))
        vp.setOrientation((0, 1, 0, 0))
        #vp.setFrustum(fieldOfView=1.0, aspect=1.0, near=0.01, far=1000)
        self.triggerRedraw(True)

    def OnButtonNewCar( self, event ):
        """Handle the wxPython event from our button"""
        # FIXME: Can we start an agent here?
        self.start_agent(Car, 'Car_' + str(self.cars),
            env=ce,
            place_args=[ 'Car', [-45.0, -2.0, 0.5], 'box', [2.0, 1.0, 1.0], [0.25, 0.0, 0.0], (15.0, 30.0), None ]
        )
        self.cars = self.cars + 1
        #e = Entity()
        #self.addCar(e)

    def OnButtonPause( self, event ):
        """Handle the wxPython event from our button"""
        if self.riding:
            self.time.pause()
        else:
            self.time.resume()
        self.riding = not self.riding

    def OnFullScreenToggle( self, event ):
        """Toggle between full and regular windows"""
        if self.returnValues:
            # return to the previous size
            posx, posy, sizex, sizey = self.returnValues
            glutReshapeWindow( sizex, sizey)
            glutPositionWindow( posx, posy )
            self.returnValues = None
        else:
            self.returnValues = (
                glutGet( GLUT_WINDOW_X ),
                glutGet( GLUT_WINDOW_Y ),
                glutGet( GLUT_WINDOW_WIDTH  ),
                glutGet( GLUT_WINDOW_HEIGHT ),
            )
            glutFullScreen( )

class MyApp(App):
    def run(self, args):
        e = PlaneEnvironment()
        ce = e.controller
        self.start_agent(TrafficLight, 'Light',
            env=ce,
            place_args=[ 'TrafficLight', [8.0, -4.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        ve = e.view
        self.start_agent(wxViewerAgent, 'EnvironmentViewer', view=ve, size=(800, 800))
        #FIXME: eva = self.start_agent(EnViewAgent, 'EnvironmentViewer', view=ve)
        #FIXME: eva.run_GUI()

if __name__ == "__main__":
    MyApp()

