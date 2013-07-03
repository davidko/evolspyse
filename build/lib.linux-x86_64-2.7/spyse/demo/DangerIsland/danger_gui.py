from spyse.asw.asw_gui import wxGameAgent
import wx
import math
import struct
import copy
import time
from spyse.core.platform.platform import Platform

#import Image

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
        wxGameAgent.setup(self,env,size)

    def app_setup(self):
        self.xChart=1000.0; self.yChart=800.0
        self.CellsOn=True
        self.make_background()
        self.make_players()
        self.SetInitialZoom()
        self.BufferImages()
    
    def ViewCells(self):
        self.smooth_init()
        self.CellsOn=not self.CellsOn
        self.draw_all()
        self.smooth_done()
        
    def smooth_draw(self,dc):
        bufdc=wx.BufferedDC(dc,self.bufferbmp)
        self.draw_background(bufdc)
        self.draw_cells(bufdc)
        self.draw_players(bufdc)

    def update_smoothly(self):
        self.smooth_init()
        self.move_players()
        self.update_cells()
        dc=wx.ClientDC(self.gamepanel)
        self.smooth_draw(dc)
        self.smooth_done()

    def load_backgroundImage(self):
        self.background_image = wx.Image("spyse/demo/DangerIsland/images/borkum_1200x900.jpg", wx.BITMAP_TYPE_JPEG)
        
    def image_by_type(self, label):
        img=None
        if label == 'Robot':
            img=wx.Image("spyse/demo/DangerIsland/images/robot.png", wx.BITMAP_TYPE_PNG)
        elif label == 'Plane':
            img=wx.Image("spyse/demo/DangerIsland/images/plane.png", wx.BITMAP_TYPE_PNG)
        else:
            try:
                img=wx.Image("spyse/demo/DangerIsland/images/" + label + ".png", wx.BITMAP_TYPE_PNG)
            except:
                pass
        if img!=None: 
            if not img.HasAlpha(): img.InitAlpha()
        return img
    
    def BufferCellsImage(self):
        width=self.BufferedBackGround.GetWidth()
        height=self.BufferedBackGround.GetHeight()
        img=wx.EmptyImage(1,1); img.SetMaskColour(0,0,0); img.InitAlpha()
        self.CellsBitmap=img.Scale(width,height).ConvertToBitmap()
        dc=wx.MemoryDC()
        dc.SelectObject(self.CellsBitmap)
        dc.SetBrush(wx.Brush("WHITE",wx.TRANSPARENT))
        pen=wx.Pen("WHITE"); dc.SetPen(pen)
        dc.SetLogicalFunction(wx.COPY)
        
        for key, value in self.env.find_items('label','cell'):
            loc=self.world2bitmap(value['location'])
            col=TYPES[value['type']]
            radius=value['radius']
            pen.SetColour(wx.Colour(col[0],col[1],col[2]))
            dc.SetPen(pen)
            dc.DrawCircle(loc[0]*self.ZoomFactor,loc[1]*self.ZoomFactor,radius*self.ZoomFactor)
#        dc.SelectObject(wx.NullBitmap)       
            
        roadmap = self.env.read('Roadmap')
#        print "Roadmap", roadmap
        nodes = roadmap['nodes']
        edges = roadmap['edges']
        for e in edges.values():
            loc0=self.world2bitmap(nodes[e[0]])
            loc1=self.world2bitmap(nodes[e[1]])
            print loc0, loc1
            pen.SetColour(wx.Colour(63, 63, 63))
            dc.SetPen(pen)
            dc.DrawLinePoint(loc0*self.ZoomFactor, loc1*self.ZoomFactor)
#            pen.SetColour(wx.Colour(192, 63, 63))
#            dc.SetPen(pen)
#            dc.DrawCircle(loc0[0]*self.ZoomFactor, loc0[1]*self.ZoomFactor, 3)
            pen.SetColour(wx.Colour(63, 192, 63))
            dc.SetPen(pen)
            dc.DrawCircle(loc1[0]*self.ZoomFactor, loc1[1]*self.ZoomFactor, 3)

        for key, value in self.env.find_items('label','sensor'):
            loc=self.world2bitmap(value['location'])
            state=value['state']
            radius=7
            pen.SetColour(wx.Colour(255, 255, 255))
            dc.SetPen(pen)
            dc.SetBrush(wx.Brush(wx.Colour(state[0], state[1], state[2])))
            dc.DrawCircle(loc[0]*self.ZoomFactor, loc[1]*self.ZoomFactor, radius*self.ZoomFactor)
            
        dc.SelectObject(wx.NullBitmap)       
            
    def BufferImages(self):
        self.BufferBackground()
        self.BufferCellsImage()
        
    def update_cells(self):
        # check if properties of cells have changed and need update in screen
        # then put a rect in update_rects
        pass

    def draw_cells(self, dc):
        if not self.CellsOn: return
        (w,h)=self.gamepanel.GetClientSizeTuple()
        rect=wx.Rect(0,0,w,h)
        mem=wx.MemoryDC()
        mem.SelectObject(self.CellsBitmap)
        for r in self.update_rects:
            if not r.Intersects(rect): continue
            dc.Blit(r.x,r.y,r.width,r.height,mem,r.x+self.Xoffs,r.y+self.Yoffs)
        mem.SelectObject(wx.NullBitmap)
        
    def make_players(self):
        ## moving objects
        self.players = {}
        for key, value in self.env.find_items('label','Robot'):
            loc=self.world2screen(value['location'])
            loc=(int(loc[0]), int(loc[1]))
            self.players[key] = Player(value['label'], self.image_by_type(value['label']), loc=loc, rot=value['rotation'], speed=value['speed'])
    
    def draw_players(self, dc):
        mem=wx.MemoryDC()
        for p in self.players.values(): 
            # draw only visible players in update_rects
            if self.VisibleRect(p.rect):
                mem.SelectObject(wx.BitmapFromImage(p.img))
                dc.Blit(p.rect.x,p.rect.y,p.rect.width,p.rect.height,mem,0,0,wx.OR)                
        mem.SelectObject(wx.NullBitmap)

    def move_players(self):
        for key, value in self.env.find_items('label','Robot'):
            if key in self.players:
                self.move_player(self.players[key], value)
            else:
                loc=self.world2screen(value['location'])
                self.players[key] = Player(value['label'], self.image_by_type(value['label']), loc=loc, rot=value['rotation'], speed=value['speed'])
        
    def move_player(self, p, e):
        new_rot = e['rotation']
        loc=self.world2screen(e['location'])
        loc=(int(loc[0]), int(loc[1]))
        x, y = p.loc
        motion_x = loc[0]-x; motion_y = loc[1]-y
        if (p.rot!=new_rot) or (motion_x!=0) or (motion_y!=0):
            oldrect=copy.copy(p.rect)
            if p.rot != new_rot: p.rot=new_rot
            p.loc=loc
            self.update_rects.append(oldrect.Union(p.rect))
        

class Player(object):
    _timer = None

    def __init__(self, label, img, loc, rot, speed):
        self.label = label            # label
        self.__img = img              # original image
        self.img = img                # rotated image
        self.rect = wx.Rect(0,0,img.GetWidth(),img.GetHeight())    # rectangle 
        self.loc = loc                # location
        self.__rot = 0                # 
        self.rot = rot                # orientation
        self.speed = speed            # speed
    
    def __get_loc(self):
        return (self.rect.x+self.rect.width/2, self.rect.y+self.rect.height/2)
     
    def __set_loc(self, loc):
        self.rect.x = loc[0]-self.rect.width/2
        self.rect.y = loc[1]-self.rect.height/2
    
    loc = property(__get_loc, __set_loc, None, "location")
    
    def __get_rot(self):
        return self.__rot
     
    def __set_rot(self, rot):
        self.__rot=rot % 360
        loc=self.loc
        self.img=self.__img.Rotate(self.__rot*(math.pi/180.0),(0,0))
        self.rect=wx.Rect(0,0,self.img.GetWidth(),self.img.GetHeight())
        self.loc=loc
    
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
        sb = wx.GetApp().GetTopWindow().statusBar
        sb.SetStatusText('', 0)
        self.__class__._timer.cancel()
