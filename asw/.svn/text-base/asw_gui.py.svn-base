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

# very simple behaviour making the agent have his own action method
class GameBehaviour(Behaviour):
    def action(self):
        self.agent.action()
        time.sleep(0.01)
        
MaxZoomFactor=8
    
class wxGameAgent(wxAgent):
    def setup(self, env, size=None):
        self.env = env
        self.size=size
        self.update_rects = []
        self.global_setup()
        self.app_setup()
        self.MakeGameFrame()
        wx.GetApp().SetTopWindow(self.frame)
        self.frame.Show()
        self.dc=wx.ClientDC(self.gamepanel)
        self.bufferbmp=wx.EmptyBitmap(size[0],size[1]) # deze beter by BufferImages zetten ? Later ToDo: resize window!
        self.gamebehaviour=GameBehaviour()
        self.add_behaviour(self.gamebehaviour)

    def MakeGameFrame(self):
        self.frame = wxGameFrame(self, -1, self.name, position=(10, 10), env=self.env, game_size=self.size)
        
    def global_setup(self):
        self.ZoomFactor=1
        self.Xoffs=0; self.Yoffs=0
        self.xChart=1.0; self.yChart=1.0
        self.paused = False
        self.time=0.0
        self.BackgroundOn=True
        self.lock=threading.Lock()
        
    def app_setup(self):
        self.GameObjects=[]
        self.make_background()
        self.SetInitialZoom()
        self.BufferImages()
        #self.make_players()
        #self.make_sensors()
        # etc..

    # override this method to create a specific background image
    def load_backgroundImage(self):
        self.background_image = wx.EmptyImage(self.size[0],self.size[1])
        
    def make_background(self):
        self.load_backgroundImage()
        w=self.background_image.GetWidth(); h=self.background_image.GetHeight()
        self.background_rect =wx.Rect(0,0,w,h)
        
    def BufferBackground(self):
        w=self.background_rect.width*self.ZoomFactor 
        h=self.background_rect.height*self.ZoomFactor 
        self.BufferedBackGround=self.background_image.Scale(w,h).ConvertToBitmap()
        
    def SetInitialZoom(self):
        self.ZoomFactor=1
        Bw=self.background_rect.width; Bh=self.background_rect.height
        while (self.ZoomFactor!=MaxZoomFactor):
            if (Bw*self.ZoomFactor<self.size[0]) or (Bh*self.ZoomFactor<self.size[1]):
                self.ZoomFactor*=2
            else: return
        
    def ToggleBackground(self):
        self.smooth_init()        
        self.BackgroundOn=not self.BackgroundOn
        self.draw_all()
        self.smooth_done()
        
        # method for updating information in statusbar
        # currently updating time and mouseposition
    def update_statusbar(self):
        tstr='time: '+str(int(self.getTime()*10)/10.0)
        self.frame.statusBar.SetStatusText(tstr,0)
        R=wx.GetMousePosition()
        (xs,ys)=self.gamepanel.ScreenToClientXY(R.x, R.y)
        (xw,yw)=self.screen2world((xs,ys))
        posstr='position: '+str(int(xw*10.0)/10.0)+','+str(int(yw*10.0)/10.0)
        self.frame.statusBar.SetStatusText(posstr,1)
    
    def getTime(self):
        return self.time
    
    def smooth_init(self):
        self.lock.acquire()
        self.update_rects = []

    def smooth_done(self):
        self.lock.release()
        
    def SlideRange(self):
        (w,h)=self.gamepanel.GetClientSizeTuple()
        Bx=self.background_rect.width; By=self.background_rect.height
        XRange=Bx*self.ZoomFactor-w 
        YRange=By*self.ZoomFactor-h 
        return (XRange, YRange)

    def SelectNewZoom(self, Hslider, Vslider, direction):
        (w, h)=self.gamepanel.GetClientSizeTuple()
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
        
        self.BufferImages()
        self.draw_all()
        self.smooth_done()
        
    def BufferImages(self):
        self.BufferBackground()
        
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
        
    def world2bitmap(self, (xw,yw)):
        Bx=float(self.background_rect.width); By=float(self.background_rect.height)
        xb=int((xw*Bx)/self.xChart); yb=int(((self.yChart-yw)*By)/self.yChart)
        return (xb, yb)
        
    def screen2world(self, (xs,ys)):
        Bx=self.background_rect.width; By=self.background_rect.height
        xw=((float(xs+self.Xoffs)*self.xChart)/Bx)/self.ZoomFactor
        yw=(1-((float(ys+self.Yoffs)/By)/self.ZoomFactor))*self.yChart
        return (xw, yw)
        
    def start(self):
        self.resume()
        
    def stop(self):
        self.gamebehaviour.set_done()
    
    def get_updates(self):
        return self.env.entities()

    def VisibleRect(self,rect):
        (w, h)=self.gamepanel.GetClientSizeTuple()
        windowrect=wx.Rect(0,0,w,h)
        if not rect.Intersects(windowrect): return False
        for r in self.update_rects: 
            if rect.Intersects(r): return True
        return False
        
    def draw_background(self, dc):
        if not self.BackgroundOn: return
        (w,h)=self.gamepanel.GetClientSizeTuple()
        rect=wx.Rect(0,0,w,h)
        mem=wx.MemoryDC()
        mem.SelectObject(self.BufferedBackGround)
        for R in self.update_rects:
            if not R.Intersects(rect): continue
            dc.Blit(R.x,R.y,R.width,R.height,mem,R.x+self.Xoffs,R.y+self.Yoffs,wx.COPY)
        mem.SelectObject(wx.NullBitmap)
            
    def smooth_draw(self, dc):
        self.draw_background(dc)
        #self.draw_players()
        #self.draw_sensors() etc.

    def draw_all(self):
        (w,h)=self.gamepanel.GetClientSizeTuple()
        self.update_rects.append(wx.Rect(0,0,w,h))
        self.smooth_draw(self.dc)
        
    def update_smoothly(self):
        self.smooth_init()
        #self.move_players()
        #self.update_sensors() etc.
        self.smooth_draw(self.dc)
        self.smooth_done()

    def UpdateWindow(self, rects):
        self.smooth_init()
        self.update_rects=rects # the damaged window regions
        self.smooth_draw(self.dc)
        self.smooth_done()
        
    def process_events(self):
        pass
    
    def action(self):
        self.process_events()
        if not self.paused:
            self.update_smoothly()
        self.update_statusbar()

class wxGamePanel(wx.Panel):
    def __init__(self, agent, *formalargs, **namedargs ):
        self.agent=agent
        wx.Panel.__init__(self,*formalargs, **namedargs)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    # return a list of damaged Rects that need to be repainted
    def GetUpdateRegionRect(self):
        Region=self.GetUpdateRegion()
        RegionRect=wx.RegionIterator(Region)
        UpdateRects=[]
        while RegionRect:
            UpdateRects.append(RegionRect.GetRect())
            RegionRect.Next()
        return UpdateRects
    
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        rects=self.GetUpdateRegionRect()
        self.agent.UpdateWindow(rects)
        

class wxGameFrame(wx.Frame):
    def __init__(self, parent, id, title, position, env, game_size):
        self.agent = parent
        self.env = env
        self.game_width, self.game_height = game_size
        wx.Frame.__init__(self, None, id, title, position, style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self)
        self.create_widgets()
        self.SetAutoLayout(True)
        self.Fit()
        self.InitSliders()
            
        
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
        self.gamepanel = wxGamePanel(self.agent, self.panel, size=wx.Size(self.game_width, self.game_height))
        self.agent.gamepanel=self.gamepanel
        
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
        
    def ToggleBackground(self, event):
        self.agent.ToggleBackground()

    def OnHslider(self, event):
        slider=event.GetEventObject()
        self.agent.SetHorOffs(slider.GetValue())
        
    def OnVslider(self, event):
        slider=event.GetEventObject()
        self.agent.SetVertOffs(slider.GetValue())

    def OnZoomIn(self, event):
        button=event.GetEventObject()
        self.agent.SelectNewZoom(self.Hslider, self.Vslider, 1)
        
    def OnZoomOut(self, event):
        button=event.GetEventObject()
        self.agent.SelectNewZoom(self.Hslider, self.Vslider, 0)

    def InitSliders(self):
        (XRange, YRange)=self.agent.SlideRange()
        self.Hslider.SetRange(0, XRange)
        self.Hslider.SetValue(self.agent.Xoffs)
        self.Vslider.SetRange(0, YRange)
        self.Vslider.SetValue(self.agent.Yoffs)
    
    def OnControlSimulation(self, event):
        """Start/Pause/Resume button pressed"""
        button = event.GetEventObject()
        if self.agent.paused():
            self.agent.resume()
            button.SetLabel('Pause')
        else:
            self.agent.pause()
            button.SetLabel('Resume')
        
    def OnPrefs(self, event):
        """Preferences button pressed"""
        self.prefs = wx.Frame(self, -1, 'Preferences', (240, 320))
        self.prefs.Show()
    
    def OnAnalyse(self, event):
        """Analyse button pressed"""
        pass

    def OnClose(self, event):
        try:
            self.agent.players.values()[0].deselect()
            self.agent.stop()
        except:
            pass
        Platform.shutdown()
        self.Destroy()
        sys.exit(0)
