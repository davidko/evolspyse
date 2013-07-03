from spyse.core.agents.wxagent import wxAgent
import wx

import os
import sys
import math
import time
import random
import copy
import threading

from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour

#from spyse.asw.analysis import AnalysisFrame

global pygame # when we import it, let's keep its proper name!
pygame = None
pygameImported = False

class wxGameAgent(wxAgent):
    def setup(self, env, size=None):
        self.env = env
        self.frame = wxGameFrame(self, -1, self.name, position=(10, 10), env=env, game_size=size)
        wx.GetApp().SetTopWindow(self.frame)
        self.frame.Show()


class wxGameFrame(wx.Frame):
    def __init__(self, parent, id, title, position, env, game_size):
        self.agent = parent
        self.env = env
        self.game_width, self.game_height = game_size
        wx.Frame.__init__(self, None, id, title, style=wx.DEFAULT_FRAME_STYLE)# & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.panel = wx.Panel(self)
        self.create_widgets()
        
        self.SetAutoLayout(True)
        self.Fit()
        
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        # 1st menu from left
        menu1 = wx.Menu()
        menu1.Append(101, "&Mercury", "This the text in the Statusbar")
        menu1.Append(102, "&Venus", "")
        menu1.Append(103, "&Earth", "You may select Earth too")
        menu1.AppendSeparator()
        menu1.Append(104, "&Close", "Close this frame")
        # 2nd menu from left
        menu2 = wx.Menu()
        menu2.Append(201, "Background")
        menu2.Append(202, "Cells")
        # a submenu in the 2nd menu
        submenu = wx.Menu()
        submenu.Append(2031, "Lanthanium")
        submenu.Append(2032, "Cerium")
        submenu.Append(2033, "Praseodymium")
        menu2.AppendMenu(203, "Lanthanides", submenu)
        # Add menus to the menu bar
        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&View")
        self.SetMenuBar(menuBar)
        # Menu events
        self.Bind(wx.EVT_MENU, self.ToggleBackground, id=201)

    def createStatusBar(self):
        self.statusBar=wx.StatusBar(self, -1)
        self.SetStatusBar(self.statusBar)
        self.statusBar.SetFieldsCount(2)
        self.statusBar.SetStatusText('time:  ',0)
        self.statusBar.SetStatusText('position: ',1)

    def createButtons(self):
        buttonbox = wx.BoxSizer(wx.HORIZONTAL)

        control_button = wx.Button(self.panel, label="Start")
        self.Bind(wx.EVT_BUTTON, self.OnControlSimulation, control_button)
        buttonbox.Add(control_button, flag=wx.ALL, border=3)

        prefs_button = wx.Button(self.panel, label="Preferences")
        self.Bind(wx.EVT_BUTTON, self.OnPrefs, prefs_button)
        buttonbox.Add(prefs_button, flag=wx.ALL, border=3)

        analysis_button = wx.Button(self.panel, label="Analysis")
        self.Bind(wx.EVT_BUTTON, self.OnAnalyse, analysis_button)
        buttonbox.Add(analysis_button, flag=wx.ALL, border=3)

        ZoomIn_button = wx.Button(self.panel, label="Zoom In")
        self.Bind(wx.EVT_BUTTON, self.OnZoomIn, ZoomIn_button)
        buttonbox.Add(ZoomIn_button, flag=wx.ALL, border=3)
        ZoomOut_button = wx.Button(self.panel, label="Zoom Out")
        self.Bind(wx.EVT_BUTTON, self.OnZoomOut, ZoomOut_button)
        buttonbox.Add(ZoomOut_button, flag=wx.ALL, border=3)
        return buttonbox
    
    def create_widgets(self):
        self.createMenuBar()
        self.createStatusBar()
            
        # game panel
        self.gamepanel = wx.Panel(self.panel, size=wx.Size(self.game_width, self.game_height))
        self.initGame()
        buttonbox=self.createButtons()
        
        #Horizontal & vertical slider bar + right button box
        self.Hslider=wx.Slider(self.panel, size=(128, -1))
        self.Bind(wx.EVT_SLIDER, self.OnHslider, self.Hslider)
        buttonbox.Add(self.Hslider)
        rightbox = wx.BoxSizer(wx.VERTICAL)
        self.Vslider=wx.Slider(self.panel, style=wx.SL_VERTICAL, size=(-1, 128))
        self.Bind(wx.EVT_SLIDER, self.OnVslider, self.Vslider)
        rightbox.Add(self.Vslider)
        
        sizer = wx.FlexGridSizer(rows=2, cols=2)
        sizer.Add(buttonbox)
        sizer.Add(wx.Panel(self))
        sizer.Add(self.gamepanel)
        sizer.Add(rightbox)

        self.panel.GetParent().SetSizer(sizer)
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)
        self.panel.Fit()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def initGame(self):
        self.agent.add_behaviour(GameInitiatorBehaviour())
        # need this for Linux compatibility
        self.game = self.gamepanel
        self.Bind(wx.EVT_IDLE, self.OnIdle)
    
    def OnIdle(self, ev):
        global pygame, pygameImported
        # import and initialise PyGame stuff

        if not pygameImported:
            if sys.platform == "win32":
                os.environ['SDL_VIDEODRIVER'] = 'windib'
            hwnd = self.gamepanel.GetHandle()
            os.environ['SDL_WINDOWID'] = str(hwnd)

            try:
                import pygame
                import pygame.locals
                pygame.display.init()
                pygameImported = True
                self.Unbind(wx.EVT_IDLE)
                
            finally:
                pass

            ## IMPORTANT: GameBehaviour can only be created now, because wx and PyGame need to initalised first!
            # this window will display the pygame-surface
            self.SetGameBehaviour()
            self.agent.add_behaviour(self.game)
            self.InitSliders()
            
    # override this methode to create an application-specific game behaviour
    def SetGameBehaviour(self):
        self.game = GameBehaviour(Frame=self, env=self.env, size=(self.game_width, self.game_height))
    
    def ToggleBackground(self, event):
        self.game.ToggleBackground()

    def OnHslider(self, event):
        slider=event.GetEventObject()
        self.game.SetHorOffs(slider.GetValue())
        
    def OnVslider(self, event):
        slider=event.GetEventObject()
        self.game.SetVertOffs(slider.GetValue())

    def OnZoomIn(self, event):
        button=event.GetEventObject()
        self.game.SelectNewZoom(self.Hslider, self.Vslider, 1)
        
    def OnZoomOut(self, event):
        button=event.GetEventObject()
        self.game.SelectNewZoom(self.Hslider, self.Vslider, 0)

    def InitSliders(self):
        (XRange, YRange)=self.game.SlideRange()
        self.Hslider.SetRange(0, XRange)
        self.Hslider.SetValue(self.game.Xoffs)
        self.Vslider.SetRange(0, YRange)
        self.Vslider.SetValue(self.game.Yoffs)
    
    def OnControlSimulation(self, event):
        """Start/Pause/Resume button pressed"""
        button = event.GetEventObject()
        if self.game.paused():
            self.game.resume()
            button.SetLabel('Pause')
        else:
            self.game.pause()
            button.SetLabel('Resume')
        
    def OnPrefs(self, event):
        """Preferences button pressed"""
        self.prefs = wx.Frame(self, -1, 'Preferences', (240, 320))
        self.prefs.Show()
    
    def OnAnalyse(self, event):
        """Analyse button pressed"""
        pass

    def OnPaint(self, event):
        self.game.update()
        
    def OnClose(self, event):
        try:
            self.game.players.values()[0].deselect()
            self.game.stop()
        except:
            pass
        Platform.shutdown()
        self.Destroy()
        sys.exit()


#---------------------------------------------------------------------------------
# Game

MaxZoomFactor=8

class GameInitiatorBehaviour(Behaviour):
    """Keep agent alive while waiting for PyGame to be initialised."""
    
    def action(self):
        if self.agent.num_behaviours()>1:
            self.set_done()
     
class GameBehaviour(Behaviour):
    """Defines the behaviour of the agents in the game."""
    
    def setup(self, Frame, env, size):
        self.Frame=Frame
        self.global_setup(env, size)
        self.app_setup()
        self.initial_draw()
        
    def initial_draw(self):
        self.smooth_init()
        self.draw_all()        
        self.smooth_done()
                
    def global_setup(self, env, size):
        self.pyGameModule=pygame
        self.ZoomFactor=1
        self.Xoffs=0; self.Yoffs=0
        self.xChart=1000.0; self.yChart=800.0
        self.__paused = True
        self.time=0.0
        self.BackgroundOn=True
        self.screen = pygame.display.set_mode(size)
        self.surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect()
        self.env = env
        self.lock=threading.Lock()
        
    def app_setup(self):
        self.GameObjects=[]
        self.make_background()
        #self.make_players()
        #self.make_sensors()
        # etc..
    
    def ToggleBackground(self):
        self.smooth_init()
        self.BackgroundOn=not self.BackgroundOn
        self.draw_all()
        self.smooth_done()
        
    def draw_all(self):
        self.update_rects.append(self.rect)
        self.smooth_draw()
        
    def smooth_draw(self):
        self.draw_background()
        #self.draw_players()
        pygame.display.update(self.update_rects)

    def update_smoothly(self):
        self.smooth_init()
        #self.move_players()
        self.smooth_draw()
        self.smooth_done()
        self.update_statusbar() # must be outside smooth_init/done pair
            
        # method for updating information in statusbar
        # currently updating time and mouseposition
    def update_statusbar(self):
        tstr='time: '+str(int(self.getTime()*10)/10.0)
        self.Frame.statusBar.SetStatusText(tstr,0)
        R=wx.GetMousePosition()
        (xs,ys)=self.Frame.gamepanel.ScreenToClientXY(R.x, R.y)
        (xw,yw)=self.screen2world((xs,ys))
        posstr='position: '+str(int(xw*10.0)/10.0)+','+str(int(yw*10.0)/10.0)
        self.Frame.statusBar.SetStatusText(posstr,1)
    
    def getTime(self):
        return self.time
    
    def smooth_init(self):
        self.lock.acquire()
        self.update_rects = []

    def smooth_done(self):
        self.lock.release()
        
    # override this method to create specific background image
    def load_backgroundImage(self):
        self.background = pygame.image.load("spyse/demo/DangerIsland/images/borkum_1200x900.jpg")
        
    def make_background(self):
        self.load_backgroundImage()
        self.background_rect = self.background.get_rect()
        self.BufferBackground()
        self.SetInitialZoom()
        
    def draw_background(self):
        if not self.BackgroundOn: return
        updateList=self.rect.collidelistall(self.update_rects)
        for i in updateList:
            R=self.update_rects[i]
            Position=(R.x, R.y)
            Area=wx.Rect(R.x+self.Xoffs,R.y+self.Yoffs,R.width,R.height)
            self.screen.blit(self.BufferedBackGround, Position,Area) 

    def BufferBackground(self):
        w=self.background_rect.width*self.ZoomFactor 
        h=self.background_rect.height*self.ZoomFactor 
        self.BufferedBackGround=pygame.transform.scale(self.background, (w,h))
        
    def SlideRange(self):
        w=self.rect.width; h=self.rect.height
        Bx=self.background_rect.width; By=self.background_rect.height
        XRange=Bx*self.ZoomFactor-w 
        YRange=By*self.ZoomFactor-h 
        return (XRange, YRange)

    def SetInitialZoom(self):
        self.ZoomFactor=1
        w=self.rect.width; h=self.rect.height
        Bw=self.background_rect.width; Bh=self.background_rect.height
        while (self.ZoomFactor!=MaxZoomFactor):
            if (Bw*self.ZoomFactor<w) or (Bh*self.ZoomFactor<h):
                self.ZoomFactor*=2
            else: return

    def SelectNewZoom(self, Hslider, Vslider, direction):
        w=self.rect.width; h=self.rect.height
        Bw=self.background_rect.width; Bh=self.background_rect.height
        zf_old=self.ZoomFactor
        if direction==1: # zoom in
            if zf_old==MaxZoomFactor: return
            zf_new=zf_old*2
            r=2.0
        else: # zoom out
            zf_new=zf_old/2
            if (zf_new*Bw<w) or (zf_new*Bh<h): return
            r=0.5
        self.smooth_init()
        self.ZoomFactor=zf_new

        xo_old=self.Xoffs; yo_old=self.Yoffs
        (XRange, YRange)=self.SlideRange()
        xo=xo_old*r+(r-1)*w/2.0
        if xo>XRange: xo=XRange
        if xo<0: xo=0
        self.Xoffs=xo
        Hslider.SetRange(0,XRange); Hslider.SetValue(xo)
        yo=yo_old*r+(r-1)*h/2.0
        if yo>YRange: yo=YRange
        if yo<0: yo=0
        self.Yoffs=yo
        Vslider.SetRange(0,YRange); Vslider.SetValue(yo)
        self.BufferBackground()
        self.draw_all()
        self.smooth_done()
        
    def SetHorOffs(self, Offset):
        self.smooth_init()
        self.Xoffs=Offset
        self.draw_all()
        self.smooth_done()
        
    def SetVertOffs(self, Offset):
        self.smooth_init()
        self.Yoffs=Offset
        self.draw_all()
        self.smooth_done()
        
    def world2screen(self, (xw,yw)):
        Bx=self.background_rect.width; By=self.background_rect.height
        xs=(xw/self.xChart)*Bx*self.ZoomFactor-self.Xoffs
        ys=(1-yw/self.yChart)*By*self.ZoomFactor-self.Yoffs
        return (xs, ys)
        
    def bitmap2world(self, (xb,yb)):
        Bx=self.background_rect.width; By=self.background_rect.height
        xw=(float(xb)*self.xChart)/Bx; yw=self.yChart-(float(yb)*self.yChart)/By
        return (xw, yw)
        
    def screen2world(self, (xs,ys)):
        Bx=self.background_rect.width; By=self.background_rect.height
        xw=((float(xs+self.Xoffs)*self.xChart)/Bx)/self.ZoomFactor
        yw=(1-((float(ys+self.Yoffs)/By)/self.ZoomFactor))*self.yChart
        return (xw, yw)
        
    def start(self):
        self.resume()
        
    def stop(self):
        self.set_done()
    
    def action(self):
        self.process_events()
        if not self.paused():
            self.update_smoothly()
        time.sleep(0.01)

    def process_events(self):
        pass
    
    def get_updates(self):
        return self.env.entities()

