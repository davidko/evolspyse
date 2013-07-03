import math
import os
from spyse.asw.environment import Controller2D, Environment2D
from roads import *
import wx

#rootdir='c:/Documents and Settings/ruizenaarmga/My Documents/LopendeProjecten/TASTE/Resource'
rootdir='c:/spyse1_0/spyse/demo/Taste_Demo'

class TasteController(Controller2D):
    
    def __init__(self, *formalargs, **namedargs):
        self.TimeScaleFactor=1
        Controller2D.__init__(self, *formalargs, **namedargs)
        
    def time(self):
        return Controller2D.time(self)*self.TimeScaleFactor
    
    # bepaal de afstand tussen twee punten
    # hemelsbreed of via de weg
    def Distance(self, Pos1, Pos2, type='ViaRoad'):
        From=self.IsOnRoad(Pos1)
        To=self.IsOnRoad(Pos2)
        S=From[2]
        return S.findBestRoute(self.roadMap,S.beginloc,S.endloc,From,To)
    
    # geef aan of positie pos op een weg ligt en geef segmentnaam terug
    # name=None: positie niet op een wegsegment
    def IsOnRoad(self, pos):
        name=None; min=20; projloc=pos; Smin=None
        for S in self.roadMap:
            found, d, proj=S.OnSegment(pos)
            if not found: continue
            if d<min:
                name=S.name; min=d; projloc=proj; Smin=S
        return (name, projloc, Smin)
        
class Object:
    def __init__(self):
        self.time=[]; self.posx=[]; self.posy=[]
        self.ti=0; self. size=0
        
    def append(self, t,posx,posy):
        self.time.append(float(t)); self.posx.append(float(posx)); self.posy.append(float(posy))
        self.size+=1
        
    def GetCurrentPos(self, t):
        N=self.size
        if N<1: return (0, 0)
        if N==1: return (self.posx[0], self.posy[0])
        while t>self.time[self.ti+1]:
            if self.ti+1<N:
                self.ti+=1
            else:
                return (self.posx[ti+1], self.posy[ti+1])
        r=(t-self.time[self.ti])/(self.time[self.ti+1]-self.time[self.ti])
        dx=self.posx[self.ti+1]-self.posx[self.ti]
        dy=self.posy[self.ti+1]-self.posy[self.ti]
        return (self.posx[self.ti]+r*dx, self.posy[self.ti]+r*dy)

class TasteEnvironment(Environment2D):
    
    def selectController(self):
        self.controller = TasteController(self.model)
        
    def setup(self):
        self.loadSensors()
        self.SetupSensorEvents()
        self.loadObjects()
        self.loadRoadmap()
        self.updateProcs.append(self.updateSensors)
        self.updateProcs.append(self.updateObjects)
        
    def loadSensors(self):
        # open file and read sensor info
        S=open(rootdir+'/Trebos/SensorSpec.txt')
        for line in S:
            name, posx, posy, type=line.split()
            self.controller.place(name, label="Sensor", location=(float(posx),float(posy)), type=type, status=0)
        S.close()
        self.SensorDetect=wx.Sound(rootdir+'/sounds/online.wav')
        
    def SetupSensorEvents(self):
        self.TimeOfEvents = []; self.EventIDs=[]
        f=open(rootdir+'/Trebos/EventList.txt')
        for line in f:
            [tstr, IDstr]=line.split()
            self.TimeOfEvents.append(float(tstr))
            self.EventIDs.append('sensor'+IDstr)
        f.close()
        self.NextEvent=0

    def loadObjects(self):
        self.objects = {}
        filelist=os.listdir(rootdir+'/Trebos/')
        for fname in filelist:
            fname=fname.upper()
            i=fname.find('.')
            if (i>6) and (fname[0:6]=='OBJECT'):
                # open file and read object trajectory
                f=open(rootdir+'/Trebos/'+fname)
                line=f.readline(); elements=line.split(); type=elements[0]
                name=fname[0:i]
                O=Object(); self.objects[name]=O
                for line in f:
                    (t, posx, posy)=line.split()
                    O.append(t,posx,posy)
                f.close()
                self.controller.place(name, label="Object", location=(O.posx[0],O.posy[0]), type=type)

    def loadRoadmap(self):
        f=open(rootdir+'/Trebos/Tetovo_Roads.txt')
        i=0; self.controller.roadMap=[]
        for line in f:
            [x1, y1, x2, y2]=line.split()
            name='RoadSegment'+str(i)
            beginloc=(int(float(x1)), int(float(y1)))
            endloc=(int(float(x2)), int(float(y2)))
            self.controller.place(name, label="Road", location=beginloc, endloc=endloc)
            self.controller.roadMap.append(RoadSegment(name,beginloc,endloc))
            i+=1
        f.close()
        
    def GetSensorEvents(self,time):
        EventList=set()
        N=len(self.EventIDs); idx=self.NextEvent
        while (idx<N) and (time>=self.TimeOfEvents[idx]):
            if (time<self.TimeOfEvents[idx]+2):
                EventList.add(self.EventIDs[idx])
            else:
                self.NextEvent+=1
            idx+=1
        return EventList

    def updateSensors(self):
        t=self.controller.time()
        ID_list=self.GetSensorEvents(t)
        for key, value in self.controller.find_items('label','Sensor'):
            e = self.controller.read(key)
            old_status=e['status']
            new_status=(key in ID_list)
            if old_status!=new_status:
                # geef een geluidsignaal dat een detectie is gedaan
                #if status: self.SensorDetect.Play(wx.SOUND_ASYNC)
                e['status']=new_status
                self.controller.write(key, e)
                
    def updateObjects(self):
        t=self.controller.time()
        for key in self.objects:
            O=self.objects[key]
            e = self.controller.read(key)
            e['location']=O.GetCurrentPos(t)
            self.controller.write(key, e)

