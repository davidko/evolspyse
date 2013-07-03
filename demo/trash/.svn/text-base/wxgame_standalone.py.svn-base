"""
Same simulation without spyse
"""


import wx
import os
import sys
import math
import threading
import time
import random

from spyse.demo.asw.analysis import AnalysisFrame

pygame = None
pygameImported = False


class GameThread(threading.Thread):
    def __init__(self, width, height):
        threading.Thread.__init__(self)
        self.__running = True
#        self.__paused = True

        # import and initialise PyGame stuff
        global pygame, pygameImported
        import pygame
        import pygame.locals
        pygame.display.init()
        self.screen = pygame.display.set_mode((width, height))
        pygameImported = True
        self.surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect()

        self.setup()

    def setup(self):
        pass

    def run(self):
        #self.update()
        while self.__running:
#            if not self.__paused:
            self.update()
            time.sleep(0.05)
        
    def update(self):
        pass
    
    def stop(self):
        self.__running = False
    
#    def pause(self):
#        self.__paused = True
#        
#    def resume(self):
#        self.__paused = False
#    
#    def paused(self):
#        return self.__paused
    

class GamePyro(GameThread):
    def __init__(self, width, height):
        GameThread.__init__(self, width, height)
        self.__paused = True
    
    def setup(self):
        self.background = pygame.Surface((self.rect.width, self.rect.height))
        self.background.fill((128, 191, 255))
        self.background_rect = self.background.get_rect()
        self.screen.blit(self.background, self.background_rect)

        #TODO: subscribe to modifications from Spyse environment via Pyro
        

class Game(GameThread):
#class GameStandalone(GameThread):
    def __init__(self, width, height):
        GameThread.__init__(self, width, height)
        self.__paused = True
        self.__update_smoothly = True
    
    def pause(self):
        self.__paused = True
        
    def resume(self):
        self.__paused = False
    
    def paused(self):
        return self.__paused

    def setup(self):
        self.surface = pygame.display.get_surface()
        #surface = surface.convert_alpha()
        
        self.make_background()
        self.draw_background()
#        self.make_cells()
#        self.draw_cells()
        self.make_objects()
        self.draw_objects()
        self.make_players()
        self.draw_players()

        pygame.display.flip()
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                #print event.pos, event.button
                for key, p in self.players.items():
                    if p.rect.contains((event.pos[0], event.pos[1], 1, 1)):
                        p.select(key)
        
        if not self.__paused:
            #TODO: receive notifications from Spyse environment via Pyro
            #TODO: determine whether full or smooth update
            if self.__update_smoothly:
                self.smooth_init()
                self.move_players()
                self.smooth_update()
            else:
                self.screen.blit(self.background, self.background_rect)
                self.move_players()
                self.draw_cells()
                self.draw_objects()
                self.draw_players()
                pygame.display.flip()

    def smooth_init(self):
        self.update_rects = []
        
    def smooth_move(self, player, motion):
        old_rect = player.rect
        player.rect = player.rect.move(motion)
        update_rect = old_rect.union(player.rect)    # assuming overlap in motion
#        self.update_rects.append(old_rect)
#        self.update_rects.append(player.rect)
        self.update_rects.append(update_rect)
    
    def smooth_update(self):
        # background
        for r in self.update_rects:
            self.screen.blit(self.background, r, r)
        
        #self.draw_cells()
        self.draw_objects()
        self.draw_players()
        pygame.display.update(self.update_rects)
#
#        # cells
#        r = 20.0
#        d = r * math.cos(30)
#        xs = self.width/(2*d)
#        ys = self.height/(r+d)
#        for x in range(0, xs, 2*d):
#            for y in range(0, ys, r+d):
#                pygame.draw.circle(surface, (31, 31, 31), x, y, r)
        
    def make_background(self):
        ## background
#        self.background = pygame.image.load("./images/borkum_plain_1200x900.png")
        self.background = pygame.image.load("./images/borkum_1200x900.jpg")
#        self.background = pygame.Surface((self.rect.width, self.rect.height))
#        self.background.fill((128, 191, 255))
        self.background_rect = self.background.get_rect()
        
    def draw_background(self):
        self.screen.blit(self.background, self.background_rect)
        
    def make_cells(self):
        ## hexagonal cells
        self.cells = []
        self.cell_radius = r = 6.0
        d = r * math.cos(30.0*math.pi/180.0)
        dd = 2*d

#        xs = int((self.rect.width+2*dd)/dd)
#        ys = int((self.rect.height+1.5*r)/(1.5*r))
#        print xs, ys
#        for xi in range(xs):
#            for yi in range(ys):
#                if yi%2 == 0:
#                    x = xi*dd
#                else:
#                    x = xi*dd+d
#                y = yi*(1.5*r)
#                cells.append((int(x), int(y)))

        xi = -1
        x = 0
        while x-d < self.rect.width:
            xi = xi+1
            yi = -1
            y = 0
            while y-r < self.rect.height:
                yi = yi+1
                if yi%2 == 0:
                    x = xi*dd
                else:
                    x = xi*dd+d
                y = yi*(1.5*r)
#                print (xi, yi), (x, y)
                self.cells.append((int(x), int(y)))
#        print len(cells), xi, yi

    def draw_cells(self):
        #TODO: draw only cells in update_rects
        r = self.cell_radius
        
        for c in self.cells:
            ## draw circles
#            pygame.draw.circle(surface, (63, 63, 63), c, int(r), 1)

            ## draw hexagons
            x = c[0]
            y = c[1]
            points = []
            for a in range(30, 360, 60):
                points.append((x + int(r*math.cos(a*math.pi/180.0)), y + int(r*math.sin(a*math.pi/180.0))))
            pygame.draw.lines(self.surface, (63, 63, 63), True, points, 1)
#            pygame.draw.aalines(surface, (63, 63, 63), True, points, True)

    def make_objects(self):
        ## static objects (sensors)
        self.objects = {}
        for i in range(640):
#            object = ('circle', (128, 128, 255), (random.randint(50, self.rect.width-50), random.randint(50, self.rect.height-50)), 6)
            object = ((128, 128, 255), (random.randint(50, self.rect.width-50), random.randint(50, self.rect.height-50)), 5, 0)
            self.objects["Sensor_" + str(i)] = object
#            pygame.draw.circle(surface, object[0], object[1], object[2], object[3])
        
    def draw_objects(self):
        # static objects (sensors)
        #TODO: draw only objects in update_rects
        for object in self.objects.values():
            pygame.draw.circle(self.surface, object[0], object[1], object[2], object[3])
        
    def make_players(self):
        ## moving objects
        self.players = {}
        for i in range(160):
            self.players["Robot_" + str(i)] = Player("robot", pygame.image.load("./images/robot.gif"), (random.randint(100, self.rect.width-100), random.randint(100, self.rect.height-100)), random.randint(0, 359), random.randint(5, 15))
        self.players["Red"] = Player("plane", pygame.image.load("./images/plane_a.gif"), (100, 240), 30, 15)
        self.players["Hot"] = Player("plane", pygame.image.load("./images/plane_b.gif"), (300, 480), 120, 15)
        self.players["Chili"] = Player("plane", pygame.image.load("./images/plane_c.gif"), (500, 120), 210, 15)
        self.players["Pepper"] = Player("plane", pygame.image.load("./images/plane_d.gif"), (700, 360), 300, 15)
        for p in self.players.values():
            self.screen.blit(p.img, p.rect)
    
    def draw_players(self):
        # players
        #TODO: draw only players in update_rects
        for p in self.players.values():
            self.screen.blit(p.img, p.rect)

    def move_players(self):
        # move the players around
        for p in self.players.values():
            rot = p.rot/180*math.pi
            motion_x = -math.sin(rot)*p.speed
            motion_y = -math.cos(rot)*p.speed
            if self.__update_smoothly:
                self.smooth_move(p, (motion_x, motion_y))
            else:
                p.rect = p.rect.move((motion_x, motion_y))
            
            old_rot = p.rot
            
            if p.type == 'robot':    # better use int constant
                p.rot = p.rot-5
            else:
                if p.rect.left < 0 or p.rect.right > self.rect.width:
                    p.rot = -p.rot
                if p.rect.top < 0 or p.rect.bottom > self.rect.height:
                    p.rot = 180-p.rot
        

class GameFrame(wx.Frame):
    def __init__(self, parent, id, title, game_size):
        self.game_width, self.game_height = game_size
        wx.Frame.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.panel = wx.Panel(self)
        self.create_widgets(self.panel)
        
        self.SetAutoLayout(True)
        self.Fit()
    
    def create_widgets(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Prepare the menu bar
        menuBar = wx.MenuBar()

        # 1st menu from left
        menu1 = wx.Menu()
        menu1.Append(101, "&Mercury", "This the text in the Statusbar")
        menu1.Append(102, "&Venus", "")
        menu1.Append(103, "&Earth", "You may select Earth too")
        menu1.AppendSeparator()
        menu1.Append(104, "&Close", "Close this frame")
        # Add menu to the menu bar
        menuBar.Append(menu1, "&Planets")

        # 2nd menu from left
        menu2 = wx.Menu()
        menu2.Append(201, "Hydrogen")
        menu2.Append(202, "Helium")
        # a submenu in the 2nd menu
        submenu = wx.Menu()
        submenu.Append(2031,"Lanthanium")
        submenu.Append(2032,"Cerium")
        submenu.Append(2033,"Praseodymium")
        menu2.AppendMenu(203, "Lanthanides", submenu)
        # Append 2nd menu
        menuBar.Append(menu2, "&Elements")

        self.SetMenuBar(menuBar)
        
        self.statusBar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.statusBar)

        # Menu events
#        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.OnMenuHighlight)
#
#        self.Bind(wx.EVT_MENU, self.Menu101, id=101)
#        self.Bind(wx.EVT_MENU, self.Menu102, id=102)
#        self.Bind(wx.EVT_MENU, self.Menu103, id=103)
#        self.Bind(wx.EVT_MENU, self.CloseWindow, id=104)
        
        
        # top buttons
#        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.btnFormat = wx.Button(self.panel, label=u'Camera Format')
#        btnSizer.Add(self.btnFormat)
#        self.btnParameter = wx.Button(self.panel, label=u'Camera Parameter')
#        btnSizer.Add(self.btnParameter)
#        sizer.Add(btnSizer)
        
        # game panel
        self.gamepanel = wx.Panel(self.panel, size=wx.Size(self.game_width, self.game_height))
        sizer.Add(self.gamepanel)
        self.initGame(self.gamepanel)
        
        # bottom buttons
        bottombox = wx.BoxSizer(wx.HORIZONTAL)

        control_button = wx.Button(self.panel, label="Start")
        self.Bind(wx.EVT_BUTTON, self.OnControlSimulation, control_button)
        bottombox.Add(control_button, flag=wx.ALL, border=3)

#        stop_button = wx.Button(self.panel, label="Stop")
#        self.Bind(wx.EVT_BUTTON, self.OnStopSimulation, stop_button)
#        bottombox.Add(stop_button, flag=wx.ALL, border=3)

        prefs_button = wx.Button(self.panel, label="Preferences")
        self.Bind(wx.EVT_BUTTON, self.OnPrefs, prefs_button)
        bottombox.Add(prefs_button, flag=wx.ALL, border=3)

        analysis_button = wx.Button(self.panel, label="Analysis")
        self.Bind(wx.EVT_BUTTON, self.OnAnalyse, analysis_button)
        bottombox.Add(analysis_button, flag=wx.ALL, border=3)

        sizer.Add(bottombox)

        panel.GetParent().SetSizer(sizer)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        panel.Fit()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
#    def initGame(self, window):
#        # this window will display the pygame-surface
#        self.hwnd = window.GetHandle()
#        if sys.platform == "win32":
#            os.environ['SDL_VIDEODRIVER'] = 'windib'
#        os.environ['SDL_WINDOWID'] = str(self.hwnd)
#        size = window.GetSize()
#        width, height = size
#        self.game = Game(width, height)
#        self.game.start()
##########################
    def initGame(self, window):
        # need this for Linux compatibility
        self.game = window
        self.Bind(wx.EVT_IDLE, self.OnIdle)
    
    def OnIdle(self, ev):
        global pygame
        
        # import and initialise PyGame stuff
        self.hwnd = self.game.GetHandle()
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.hwnd)

        try:
            import pygame
            import pygame.locals
            pygame.display.init()
            
            size = self.game.GetSize()
            width, height = size
            self.game = Game(width, height)
            self.game.start()

            self.Unbind(wx.EVT_IDLE)
        finally:
            pass
##########################
#    def OnStartSimulation(self, event):
#        """Start button pressed"""
#        print 'Start', event
#        self.game.start()
        
    def OnControlSimulation(self, event):
        """Start/Pause/Resume button pressed"""
        button = event.GetEventObject()
        if self.game.paused():
            self.game.resume()
            button.SetLabel('Pause')
        else:
            self.game.pause()
            button.SetLabel('Resume')
        
#    def OnStopSimulation(self, event):
#        """Stop button pressed"""
#        print 'Stop', event
#        self.game.stop()
        
#    def OnSize(self, event):
#        size = self.GetClientSize()
#        print 'resizing', size
#        if getattr(self, 'app', None):
#            self.app.update()
#        event.Skip()

    def OnPrefs(self, event):
        """Preferences button pressed"""
        self.prefs = wx.Frame(self, -1, 'Preferences', (240, 320))
        self.prefs.Show()
    
    def OnAnalyse(self, event):
        """Analyse button pressed"""
        self.analyse = AnalysisFrame(self, -1, 'Analysis', (240, 320))
        self.analyse.Show()
    
    def OnPaint(self, event):
        self.game.update()
        
    def OnClose(self, event):
        self.game.stop()
        try:
            self.game.players.values()[0].deselect()
        except:
            pass
        self.Destroy()
        sys.exit()


class Player(object):
    _timer = None

    def __init__(self, type, img, loc, rot, speed):
        self.type = type              # type
        self.__img = img              # original image
        self.img = img                # rotated image
        self.rect = img.get_rect()    # rectangle 
        self.loc = loc                # location
        self.__rot = 0                # 
        self.rot = rot                # orientation
        self.speed = speed            # speed
    
    def __get_loc(self):
        return self.rect.center
     
    def __set_loc(self, loc):
        self.rect.center = loc
    
    loc = property(__get_loc, __set_loc, None, "location")
    
    def __get_rot(self):
        return self.__rot
     
    def __set_rot(self, rot):
        self.__rot = math.fmod(rot, 360)
        old_center = self.rect.center
        self.img = pygame.transform.rotate(self.__img, self.__rot)
        self.rect = self.img.get_rect()
        self.rect.center = old_center
    
    rot = property(__get_rot, __set_rot, None, "rotation")
    
    def select(self, title):
        sb = wx.GetApp().GetTopWindow().statusBar
        t = time.strftime("%H:%M:%S", time.localtime())
        sb.SetStatusText(t + ': ' + title + ' @ ' + str(self.loc), 0)

        frame = wx.Frame(None, -1, title, (240, 320))
        frame.Show()
        frame.SetFocus()

        try:
            self.__class__._timer.cancel()
        except:
            print 'failed'
            pass
        self.__class__._timer = threading.Timer(5.0, self.deselect)
        self.__class__._timer.start()
        
    def deselect(self):
        print 'deselect'
        sb = wx.GetApp().GetTopWindow().statusBar
        sb.SetStatusText('', 0)
        self.__class__._timer.cancel()
        
#        frame = wx.Frame(None, -1, title, (240, 320))
#        wx.GetApp().SetTopWindow(frame)
#        frame.Show()
        
import Pyro.core
import time

if __name__ == '__main__':

## get Pyro proxy to the environment
#    lv_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
#    asw_view = Pyro.core.getProxyForURI("PYROLOC://localhost:9000/asw-view")
#    entities = asw_view.entities()
#    print entities
    
    
    app = wx.PySimpleApp(0)
    frame = GameFrame(None, -1, "Danger Island", (1200, 900))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
