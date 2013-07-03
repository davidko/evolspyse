from spyse.asw.asw_gui import *
#from spyse.core.agents.wxagent import wxAgent
import wx

#import os
#import sys
#import math
#import time
#import random
#import copy
#import threading

from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour

global pygame

import Image
TYPES = { # type: (red, green, blue)
         'city':     (255,   0,   0),
         'grass':    (  0, 255,   0),
         'sea':      (  0,   0, 255),
         'sand':     (255, 255, 255),
         'airport':  (127, 127, 127),
         'road':     (  0,   0,   0)
        }


class DI_GameAgent(wxGameAgent):
    def setup(self, env, size=None):
        self.env = env
        self.frame = DI_GameFrame(self, -1, self.name, position=(10, 10), env=env, game_size=size)
        wx.GetApp().SetTopWindow(self.frame)
        self.frame.Show()


class DI_GameFrame(wxGameFrame):
   
    def SetGameBehaviour(self):
        self.game = DI_Behaviour(Frame=self, env=self.env, size=(self.game_width, self.game_height))
            
    def ViewCells(self, event):
        self.game.ViewCells()


#---------------------------------------------------------------------------------
# Game

MaxZoomFactor=8

class DI_Behaviour(GameBehaviour):
    """Defines the behaviour of the agents in the Danger Islands game."""
    
    def app_setup(self):
        global pygame
        pygame=self.pyGameModule
        self.CellsOn=True
        self.make_background()
        self.make_cells()
        self.make_players()
    
    def ViewCells(self):
        self.smooth_init()
        self.CellsOn=not self.CellsOn
        self.draw_all()
        self.smooth_done()
                
    def smooth_draw(self):
        self.draw_background()
        self.draw_cells()
        self.draw_players()
        pygame.display.update(self.update_rects)
        
    def update_smoothly(self):
        self.smooth_init()
        self.move_players()
        self.update_cells()
        self.smooth_draw()
        self.smooth_done()
        self.update_statusbar()
    
    def load_backgroundImage(self):
        self.background = pygame.image.load("spyse/demo/DangerIsland/images/borkum_1200x900.jpg")
        
    def image_by_type(self, label):
        if label == 'Robot':
            return pygame.image.load("spyse/demo/DangerIsland/images/robot.png")
        elif label == 'Plane':
            return pygame.image.load("spyse/demo/DangerIsland/images/plane.png")
        else:
            try:
                return pygame.image.load("spyse/demo/DangerIsland/images/" + label + ".png")
            except:
                return None
        
    def __colour2type(self, r, g, b):
        d = []
        for t, c in TYPES.iteritems():
            dx = r-c[0]; dy = g-c[1]; dz = b-c[2]
            d.append((math.sqrt(dx*dx + dy*dy + dz*dz), t))
        return min(d)[1]

    #TODO: registreren van cells in environment
    # (eigenlijk moet het andersom)
    def make_cells(self):
        im = Image.open("spyse/demo/DangerIsland/images/borkum_plain_1200x900.png")
        width, height = im.size
        data = im.getdata()
        ## hexagonal cells
        self.cells = []
        self.cell_radius = rad = 9.0
        dia = rad * math.cos(30.0*math.pi/180.0)
        dd = 2*dia

        xi = 0
        x = 0
        while x < width:
            yi = 0
            y = 0
            while y < height:
                if yi%2 == 0:
                    x = xi*dd
                else:
                    x = xi*dd+dia

                i = int(y)*width+int(x)
                r, g, b, a = data[i]
                t = self.__colour2type(r, g, b)
                self.cells.append((self.bitmap2world((x, y)), t))
#                if xi<2: print (xi, yi), (x, y)
                
                yi = yi+1
                y = yi*(1.5*rad)
            xi = xi+1

    def update_cells(self):
        # check if properties of cells have changed and need update in screen
        # then put a rect in update_rects
        for c in self.cells:
            pass

    def draw_cells(self):
        if not self.CellsOn: return
        r = max(3, int(self.cell_radius*self.ZoomFactor))
        crect=pygame.Rect(0,0,2*r,2*r)
        for c in self.cells:
            loc=self.world2screen(c[0])
            crect.centerx, crect.centery=loc[0], loc[1]
            # draw only visible cells in update_rects
            if self.rect.colliderect(crect) and (crect.collidelist(self.update_rects)>=0):
                col = TYPES[c[1]]
                ## draw circles
                pygame.draw.circle(self.surface, col, (int(loc[0]),int(loc[1])), r, 1)

      
    def make_players(self):
        ## moving objects
        self.players = {}
        entities = self.env.entities()
        for entity in entities:
            e = self.env.read(entity)
            if e['label'] == 'Robot':
                loc=self.world2screen(e['location'])
                self.players[entity] = Player(e['label'], self.image_by_type(e['label']), loc=loc, rot=e['rotation'], speed=e['speed'])
    
    def draw_players(self):
        for p in self.players.values(): 
            # draw only visible players in update_rects
            if self.rect.colliderect(p.rect) and (p.rect.collidelist(self.update_rects)>=0):
                self.screen.blit(p.img, p.rect) 

    def move_players(self):
        entities = self.get_updates()
        for entity in entities:
            e = self.env.read(entity)
            if e['label'] == 'Robot':
                if entity in self.players:
                    self.move_player(self.players[entity], e)
                else:
                    loc=self.world2screen(e['location'])
                    self.players[entity] = Player(e['label'], self.image_by_type(e['label']), loc=loc, rot=e['rotation'], speed=e['speed'])

    def move_player(self, p, e):
        new_rot = e['rotation']; loc=self.world2screen(e['location'])
        x, y = p.loc
        motion_x = loc[0]-x; motion_y = loc[1]-y
        if (p.rot!=new_rot) or (motion_x!=0) or (motion_y!=0):
            self.update_rects.append(p.rect)
            if p.rot != new_rot: p.rot=new_rot
            p.rect = p.rect.move((motion_x, motion_y))
            self.update_rects.append(p.rect)
        

#TODO: nagaan of player een subclass van sprite kan zijn
# sprite bevat de mogelijkheden om om te gaan met bewegingen over een achtergrond
class Player(object):
    _timer = None

    def __init__(self, label, img, loc, rot, speed):
        self.label = label            # label
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
        self.__rot = rot % 360
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


