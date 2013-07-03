#!/usr/bin/env python

"""Spyse traffic jam demo for semant"""

import math

from spyse.core.agents.agent import Agent
from spyse.core.agents.tkagent import TkinterAgent
from spyse.core.agents.wxagent import wxAgent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour
from spyse.core.semant.semant import Semant
from spyse.core.semant.environment import PlaneEnvironment
from spyse.app.app import App

from datetime import datetime

from Tkinter import *

import wx

### OpenGL initialisation

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

#        self.frame = wxAgentFrame(None, -1, name, position=(10, 10), size=(width, height))
#        self.create_widgets(self.frame)
#        self.frame.Show(True)

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
        frame.context = SimulationContext(frame)
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

class EnViewAgent(TkinterAgent):
    zoom = 4
    width = 100
    height = 100
    i = 0    # remove

    def setup(self, view):
        self.__view = view
        self.__datastore = {}
        self.add_behaviour(DrawEnvironmentBehaviour(view=self.__view))

    def create_widgets(self, frame):
        frame.title(self.name + " - Environment")

        # create canvas for drawing entities in the environment
        self.canvas = Canvas(frame)
        self.canvas["background"] = "#FFFFFF"
        self.canvas["borderwidth"] = 1
        self.canvas["width"] = self.zoom * self.width
        self.canvas["height"] = self.zoom * self.height

        self.canvas.create_rectangle(0, self.zoom * 23, self.zoom * self.width, self.zoom * 27, fill="#777777", stipple="gray25", width=0)
        self.canvas.create_rectangle(0, self.zoom * 73, self.zoom * self.width, self.zoom * 77, fill="#777777", stipple="gray25", width=0)

        #self.canvas.create_rectangle(20, 20, 190, 190, fill="#FF7733")
        # start=0 ==> 3 o'clock
        # extent=width of wedge, counter-clockwise
        # start = h + a/2
        # extent = a
        #self.canvas.create_arc(0,0,200,200, start=0, extent=30, fill="#3377AA", stipple="gray50", width=1)
        #self.canvas.create_arc(200,200,400,400, start=180, extent=45, fill="#226699", stipple="gray50", width=1)

        self.canvas.pack()

#        button1 = Button(frame, command=self.test)
#        button1["text"]="Test"
#        button1.pack()
        button1 = Button(frame, command=self.reset)
        button1["text"]="Reset"
        button1.pack()

    def test(self):
        self.i = self.i + 1
        self.canvas.create_rectangle(self.i*10, self.i*20, self.i*30, self.i*40, fill="#3377AA", width=0, stipple="gray25", tags=["test"])

    def reset(self):
        all = self.canvas.find_all()
        for a in all:
            self.canvas.delete(a)
        self.canvas.create_rectangle(0, self.zoom * 23, self.zoom * self.width, self.zoom * 27, fill="#777777", stipple="gray25", width=0)
        self.canvas.create_rectangle(0, self.zoom * 73, self.zoom * self.width, self.zoom * 77, fill="#777777", stipple="gray25", width=0)
        return
        entities = self.__view.entities()
        for e in entities:
            if e.name == 'Car1':
                e.x =  05
                e.y =  25
                e.h =   0
                e.v =   2
                # controller.write(e)    ???
            elif e.name == 'Car2':
                e.x =  95
                e.y =  25
                e.h = 180
                e.v =   1
            elif e.name == 'Car4':
                e.x =  05
                e.y =  75
                e.h =   0
                e.v =   2
            elif e.name == 'Car5':
                e.x =  05
                e.y =  75
                e.h =   0
                e.v =   1

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

class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        # initial mouse position
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.GetContext():
            self.SetCurrent()
            glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseDown(self, evt):
        self.CaptureMouse()


    def OnMouseUp(self, evt):
        self.ReleaseMouse()


    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.x, self.y = self.lastx, self.lasty
            self.x, self.y = evt.GetPosition()
            self.Refresh(False)

class CubeCanvas(MyCanvasBase):
    def InitGL(self):
        # set viewing projection
        glMatrixMode(GL_PROJECTION);
        glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0);

        # position viewer
        glMatrixMode(GL_MODELVIEW);
        glTranslatef(0.0, 0.0, -2.0);

        # position object
        glRotatef(self.y, 1.0, 0.0, 0.0);
        glRotatef(self.x, 0.0, 1.0, 0.0);

        glEnable(GL_DEPTH_TEST);
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        # draw six faces of a cube
        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)

        glNormal3f( 0.0, 0.0,-1.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)

        glNormal3f( 0.0, 1.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5, 0.5)

        glNormal3f( 0.0,-1.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)

        glNormal3f( 1.0, 0.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glEnd()

        glRotatef((self.lasty - self.y)/100., 1.0, 0.0, 0.0);
        glRotatef((self.lastx - self.x)/100., 0.0, 1.0, 0.0);

        self.SwapBuffers()

class ConeCanvas(MyCanvasBase):
    def InitGL( self ):
        glMatrixMode(GL_PROJECTION);
        # camera frustrum setup
        glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0);
        glMaterial(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterial(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterial(GL_FRONT, GL_SPECULAR, [1.0, 0.0, 1.0, 1.0])
        glMaterial(GL_FRONT, GL_SHININESS, 50.0)
        glLight(GL_LIGHT0, GL_AMBIENT, [0.0, 1.0, 0.0, 1.0])
        glLight(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLight(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0]);
        glLightModel(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # position viewer
        glMatrixMode(GL_MODELVIEW);

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        # use a fresh transformation matrix
        glPushMatrix()
        # position object
        glTranslate(0.0, 0.0, -2.0);
        glRotate(30.0, 1.0, 0.0, 0.0);
        glRotate(30.0, 0.0, 1.0, 0.0);

        glTranslate(0, -1, 0)
        glRotate(250, 1, 0, 0)
        glutSolidCone(0.5, 1, 30, 5)
        glPopMatrix()
        glRotatef((self.lasty - self.y)/100., 0.0, 0.0, 1.0);
        glRotatef(0.0, (self.lastx - self.x)/100., 1.0, 0.0);
        # push into visible buffer
        self.SwapBuffers()

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

class wxTestAgent(wxAgent):
    def setup(self):
        self.add_behaviour(DummyBehaviour())

    def create_widgets(self, frame):
        #wx.Frame.__init__(self, parent, 2400, "I've been driving in my car, it's not quite a Jaguar", size=(800,600) )
        outerbox = wx.BoxSizer(wx.VERTICAL)
        glbox = wx.BoxSizer(wx.VERTICAL)
        outerbox.Add( glbox, 5, wx.EXPAND )
        tID = wx.NewId()
        frame.context = SimulationContext(frame)
        glbox.Add(frame.context, 1, wx.EXPAND )

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        outerbox.Add( buttonbox, 0, wx.FIXED_MINSIZE)
        buttonbox.Add(wx.Button(frame, 1003, "Reset View"), 0)
        wx.EVT_BUTTON(frame, 1003, frame.context.OnButtonResetView)
        buttonbox.Add(wx.Button(frame, 1004, "Add Car"), 0)
        wx.EVT_BUTTON(frame, 1004, frame.context.OnButtonNewCar)
        buttonbox.Add(wx.Button(frame, 1005, "Pause"), 0)
        wx.EVT_BUTTON(frame, 1005, frame.context.OnButtonPause)
        frame.SetAutoLayout(True)
        frame.SetSizer( outerbox )

    def create_widgets_old(self, frame):
#        frame.window = wx.Panel(frame)
#        frame.window = MyFloat(frame)
        if self.name == 'Cube':
            canvas = CubeCanvas(frame)
        elif self.name == 'Cone':
            canvas = ConeCanvas(frame)
        elif self.name == 'Text':
            # http://www.wxpython.org/docs/howto/node13.html
            frame.control = wx.TextCtrl(frame, 1, style=wx.TE_MULTILINE)
            frame.CreateStatusBar() # A Statusbar in the bottom of the window
            # Setting up the menu.
            filemenu= wx.Menu()
            filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
            filemenu.AppendSeparator()
            filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
            # Creating the menubar.
            menuBar = wx.MenuBar()
            menuBar.Append(filemenu,"&File")            # Adding the "filemenu" to the MenuBar
            frame.SetMenuBar(menuBar)                    # Adding the MenuBar to the Frame content.
            wx.EVT_MENU(frame, wx.ID_ABOUT, self.OnAbout)    # attach the menu-event ID_ABOUT to the 
                                                        # method frame.OnAbout
            wx.EVT_MENU(frame, wx.ID_EXIT, self.OnExit)    # attach the menu-event ID_EXIT to the
                                                        # method frame.OnExit
            frame.Show(True)

    def OnAbout(self, e):
        #d = wx.MessageDialog(frame, " A sample editor in wxPython", "About Sample Editor", wxOK)
        d = wx.MessageDialog(frame, " A sample editor \n"
            " in wxPython","About Sample Editor", wxOK)    # Create a message dialog box
        d.ShowModal()                                    # Shows it
        d.Destroy()                                        # finally destroy it when finished.

    def OnExit(self, e):
        frame.Close(True)                        # Close the frame.
        # FIXME?: shut down platform

class MyApp(App):
    def run(self, args):
        #self.start_agent(SubscriptionAgent, 'Red')

        e = PlaneEnvironment()
        ce = e.controller

        #ce.place('A', 'Agent', 20, 40, 45)
        #ce.place('B', 'Agent', 60, 80, 0)
        #ce.place('C', 'Agent', 40, 30, 180)
        #ce.move('A', x=60)
        #ce.move('A', y=40)
        #ce.forward('A', 20)
        #
        #print 'A.x', ce.read('A').x
        #print 'A.y', ce.read('A').y
        #print 'B.x', ce.read('B').x
        #print 'B.y', ce.read('B').y
        #print 'C.x', ce.read('C').x
        #print 'C.y', ce.read('C').y
        #
        #print ce.neighbours('A', 30)
        #print ce.inview('A', 30, 60)

        #class MyFloat(FloatCanvas):
        #    def __init__(self, frame):
        #        FloatCanvas.__init__(self, frame, -1, Debug = 0, BackgroundColor = "DARK SLATE BLUE")
        #        #Canvas = frame.Canvas
        #        self.AddLine(((-200, -100), (200, 100), (200, -100), (-200, 100)), LineWidth = 3, LineColor = 'white')
        #        self.AddCircle(0, 0, 200, LineWidth = 1, LineColor = 'yellow')
        #        #self.ZoomToBB()
        #
        #class MyPanel(wx.Panel):
        #    def __init__(self, frame):
        #        wx.Panel.__init__(self, frame, -1, Debug = 0, BackgroundColor = "DARK SLATE BLUE")

        # drop into the standard Python debugger, works on Windows, at least
        #import pdb; pdb.set_trace()

        #self.start_agent(wxTestAgent, 'Cube')
        #self.start_agent(wxTestAgent, 'Cone')
        #name, type, spot=[0, 0, 0], form='box', size=[0, 0, 0], velo=[0, 0, 0], view=(10, 90), cond=None
        self.start_agent(TrafficLight, 'Light',
            env=ce,
            place_args=[ 'TrafficLight', [8.0, -4.0, 0.0], 'box', [2.0, 1.0, 1.0], [-1.0, -0.25, 0.0], (15.0, 90.0), 'green' ]
        )
        #self.start_agent(Car, 'FastCar',
        #    env=ce,
        #    place_args=[ 'Car', [-45.0, -1.5, 0.5], 'box', [2.0, 1.0, 1.0], [0.5, 0.0, 0.0], (15.0, 45.0), None ]
        #)
        #self.start_agent(Car, 'SlowCar',
        #    env=ce,
        #    place_args=[ 'Car', [-30.0, -1.5, 0.5], 'box', [2.0, 1.0, 1.0], [0.25, 0.0, 0.0], (15.0, 45.0), None ]
        #)
        #self.start_agent(Car, 'ThirdCar',
        #    env=ce,
        #    place_args=[ 'Car', [-75.0, -1.0, 0.5], 'box', [2.0, 1.0, 1.0], [0.75, 0.0, 0.0], (10.0, 90.0), None ]
        #)

        ve = e.view
        self.start_agent(wxViewerAgent, 'EnvironmentViewer', view=ve, size=(800, 800))
        #FIXME: eva = self.start_agent(EnViewAgent, 'EnvironmentViewer', view=ve)
        #FIXME: eva.run_GUI()

if __name__ == "__main__":
    MyApp()

