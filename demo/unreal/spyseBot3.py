#!/usr/bin/python

"""Spyse demo"""

import spyse
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour
from spyse.core.semant.semant import Semant
from spyse.util.vector import vector
from spyse.app.app import App

import math
import copy
import string
import socket
import time
import random
from Tkinter import *

HOST = 'localhost'
PORT = 3000

class UTEntity(object):
    def __init__(self, type=None, id=None, name=None, team=None, location=None, rotation=None, velocity=None, health=None, weapon=None, reachable=None, cls=None, stamp=None, tme=None):
        self.type = type
        self.id = id
        self.name = name
        self.team = team
        self.location = location
        self.rotation = rotation
        self.velocity = velocity
        self.health = health
        self.weapon = weapon
        self.reachable = reachable
        self.cls = cls
        self.stamp = stamp
        self.tme=tme

class UTEvent(object):
    def __init__(self, type=None, id=None, name=None, location=None, normal=None, damage=None, damageType=None, cls=None, stamp=None):
        self.type = type
        self.id = id
        self.name = name
        self.location = location
        self.normal = normal
        self.damage = damage
        self.damageType = damageType
        self.cls = cls
        self.stamp = stamp

class UTObservation(object):
    def __init__(self):
        self.entities = []
        self.events = []

        self.reachables = ['NAV','DOM','MOV','INV','FLG','PLR']
        self.messages = ['VMS','VMT','VMG']
        self.zoneChange = ['ZCF','ZCH','ZCB']
        self.observation = ['HRP','HRN','SEE', 'PRJ']
        self.bumps = ['WAL','FAL','BMP']

    def addEnt(self, type, cont, tme):
        if type in self.reachables:
            i = string.find(cont, 'Id')+3
            j = string.find(cont, '}', i)
            id = cont[i:j]

            location = [0,0,0]
            i = string.find(cont, 'Location')+ 9
            k = string.find(cont, ',', i)
            l = string.find(cont, ',', k+1)
            j = string.find(cont, '}', l)
#            print i, j, k, l
            location[0] = string.atof(cont[i:k])
            location[1] = string.atof(cont[k+1:l])
            location[2] = string.atof(cont[l+1:j])

            i = string.find(cont, 'Reachable')+10
            j = string.find(cont, '}', i)
            if cont[i:j] == 'True':
                reachable = True
            else:
                reachable = False

#            print "Entity Added: ", type, name, location, reachable
            entity = UTEntity(type=type, id=id, location=location, reachable=reachable, stamp=time.time())
            self.entities.append(entity)

        elif type is 'SLF': 
            i = string.find(cont, 'Id')+3
            j = string.find(cont, '}', i)
            id = cont[i:j]

            i = string.find(cont, 'Name')+5
            j = string.find(cont, '}', i)
            name = cont[i:j]

            i = string.find(cont, 'Team')+5
            j = string.find(cont, '}', i)
            team = cont[i:j]

            location = [0,0,0]
            i = string.find(cont, 'Location')+ 9
            k = string.find(cont, ',', i)
            l = string.find(cont, ',', k+1)
            j = string.find(cont, '}', l)
            location[0] = string.atof(cont[i:k])
            location[1] = string.atof(cont[k+1:l])
            location[2] = string.atof(cont[l+1:j])
#            print "Self: Location ", location

            i = string.find(cont, 'Rotation')+9
            k = string.find(cont, ',', i)
            l = string.find(cont, ',', k+1)
            j = string.find(cont, '}', l)
            rotation = [string.atof(cont[i:k]),string.atof(cont[k+1:l]),string.atof(cont[l+1:j])]

            #velocity
            i = string.find(cont, 'Velocity')+9
            k = string.find(cont, ',', i)
            l = string.find(cont, ',', k+1)
            j = string.find(cont, '}', l)
            velocity = [string.atof(cont[i:k]),string.atof(cont[k+1:l]),string.atof(cont[l+1:j])]

            #health
            i = string.find(cont, 'Health')+7
            j = string.find(cont, '}', i)
            health = string.atof(cont[i:j])

            #weapon
            i = string.find(cont, 'Weapon')+7
            j = string.find(cont, '}', i)
            weapon = cont[i:j]

            #game time
            #=tme

            #comp time
            now = time.time()
#            print "New Self!!!", tme, now
            entity = UTEntity(type=type, id=id, name=name, team=team, location=location, rotation=rotation, velocity=velocity, health=health, weapon=weapon, stamp=now, tme=tme)
#            self.but.append(entity)
            self.entities.append(entity)

    def addEvent(self, type, cont):
#        print "Add Event"
        if type == 'NFO':
            event = UTEvent(type=type)
            self.events.append(event)
#            print "event added", self.events 
        elif type is 'AIN':
            i = string.find(cont, 'Id')+3
            j = string.find(cont, '}', i)
            id = cont[i:j]

            i = string.find(cont, 'Class')+6
            j = string.find(cont, '}', i)
            cls = cont[i:j]

            event = UTEvent(type=type, id=id, cls=cls, stamp=time.time())
            self.events.append(event)
        elif type in self.messages:
            print "Received Message:", cont
        elif type in self.zoneChange:
            pass
        elif type in self.bumps:
            for event in self.events:
                if event.type is type:
                    self.removeEvent(event)

            i = string.find(cont, 'Id')+3
            j = string.find(cont, '}', i)
            id = cont[i:j]

            location = [0,0,0]
            i = string.find(cont, 'Location')+ 9
            k = string.find(cont, ',', i)
            l = string.find(cont, ',', k+1)
            j = string.find(cont, '}', l)
            location[0] = string.atof(cont[i:k])
            location[1] = string.atof(cont[k+1:l])
            location[2] = string.atof(cont[l+1:j])
            #normal

            event = UTEvent(type=type, id=id, location=location, stamp=time.time())
            self.events.append(event)
        elif type in self.observation:
            pass
        elif type is 'DIE':
            self.events.append(UTEvent(type=type), stamp=time.time())
        elif type is 'DAM':
            pass
        elif type is 'HIT':
            pass
        elif type is ('PTH' or 'RCH'):
            pass
        elif type is 'FIN':
            pass

    def clearEnt(self):
        self.entities = []
    def clearEvents(self):
        self.events = []
    def removeEnt(self, ent):
        return self.entities.remove[e]
    def removeEvent(self, event):
        return self.events.remove(event)

#Message parser
class UTMessage(object):
    def __init__(self, model):
        self.buffer = ''

        self.synctypes = ['BEG', 'SLF', 'GAM', 'PLR', 'NAV', 'MOV', 'DOM', 'FLG', 'INV', 'END']
        self.asynctypes = ['NFO', 'AIN', 'VMS', 'VMT', 'VMG', 'ZCF', 'ZCH', 'ZCB', 'CWP', 'WAL', 'FAL', 'BMP', 'HRP', 'HRN', 'SEE', 'PRJ', 'KIL', 'DIE', 'DAM', 'HIT', 'PTH', 'RCH','FIN']
        self.model = model
        self.index = 0
        self.parsing = True

    def parse(self):
#        print "Parse"
#        if self.buffer is not '':
#            print self.buffer
#        buf = copy.deepcopy(self.buffer)

        j = string.rfind(self.buffer, 'END')
        i = string.rfind(self.buffer, 'BEG', 0, j)
        if (i != -1) and (j != -1):
            type = self.buffer[i:i+3]
            cont = self.buffer[i+4:j]
            self.syncMessageHandling(type,cont)

        parsing = True
        i = 0        
        while parsing == True:
            if self.buffer[i:i+3] in self.asynctypes:
                j = string.find(self.buffer, '\n')
                if j != -1:
                    type = self.buffer[i:i+3]
                    cont = self.buffer[i+4:j]
                    self.asyncMessageHandling(type, cont)
#                    print "Type: ", self.buffer[i:i+3]
#                    print "Cont: ", self.buffer[i+4:j]
                    self.buffer = self.buffer[j+1:]
                else:
                    parsing = False

            elif self.buffer[i:i+3] == 'BEG':
                j = string.find(self.buffer, 'END')
                if j != -1:
#                    type = self.buffer[i:i+3]
#                    cont = self.buffer[i+4:j]
#                    self.syncMessageHandling(type,cont)
#                    print "Type: ", self.buffer[i:i+3]
#                    print "Cont: ", self.buffer[i+4:j]
                    self.buffer = self.buffer[j+4:]
                else: 
                    self.parsing = False
            else:
#                print self.buffer[:]
                while ((self.buffer[i:i+3] not in self.asynctypes) and (self.buffer[i:i+3] != 'BEG') and (len(self.buffer) != i)):
                    i = i+1
                self.buffer = self.buffer[i:]
                parsing = False


    def syncMessageHandling(self,sync,msg):
        self.model.clearEnt()

        i = string.find(msg, 'Time')+5
        j = string.find(msg, '}', i)
        time = string.atof(msg[i:j])

        for type in self.synctypes:
            r = string.find(msg, type)
            while r is not -1:
                s = string.find(msg, '\n', r)
                if s is not -1:
                    cont = msg[r:s]
                    if type in self.synctypes:
                        self.model.addEnt(type, cont, time)
                r = string.find(msg, type, s)

    def asyncMessageHandling(self,type,msg):
        self.model.addEvent(type,msg)

    def appendToBuffer(self, data):
        self.buffer = self.buffer+data

#Observe behaviour
class ObserveBehaviour(Behaviour):
    def setup(self):
        self.msg = self.datastore["msg"]

    def action(self):
        self.msg.parse()
        self.result = '1'

#Orient behaviour
class OrientBehaviour(Behaviour):
    def setup(self):
        self.msg = self.datastore["msg"]

    def action(self):
#        print "Orient"
#        print self.datastore["status"]
        now = time.time()

        self.datastore["visible"] = []
        self.datastore["reachable"] = []
        self.datastore["new"] = []

        for ent in self.datastore["observation"].entities:
            if ent.type is 'SLF':
                self.datastore["self"] = ent
                sf = ent
            else:
                self.datastore["visible"].append(ent)
                if ent.reachable == True:
                    self.datastore["reachable"].append(ent)
                    if ent not in self.datastore["explored"]:
                        self.datastore["new"].append(ent)

        for ev in self.datastore["observation"].events:
            if ev.type in self.datastore["bumps"]:
                if self.datastore["interference-time"] is not ev.stamp:
                    self.datastore["interference-time"] = now
                if self.datastore["interference"] is False:
                    if (now - ev.stamp < 0.2):
                        location = self.datastore["self"].location
                        interloc = ev.location

                        s = vector.Vector(location)
                        t = vector.Vector(interloc)
                        dist = vector.norm(t) - vector.norm(s)
                        print "Interdist: ", dist
                        if dist < 20:
                            print "Interference!!!!!!!!!!"
                            self.datastore["interference"] = True

        if (now - self.datastore["selected-time"] > 12):
            self.datastore["status"] = 'TimedOut'
            self.datastore["status-time"] = now

        elif (now - self.datastore["selected-time"] > 6):
            if self.datastore["status"] is not 'Interference' and self.datastore["interference-once"] is False:
                self.datastore["status"] = 'Interference'
                self.datastore["status-time"] = now
                self.datastore["interference-once"] = True

        if (self.datastore["status"] == 'TimedOut'):
            self.datastore["status"] = 'FullTurn'
            self.datastore["status-time"] = now

        elif (self.datastore["status"] == 'Reached'):
            print "Target Reached!!"
            self.datastore["status"] = 'Select'
            self.datastore["status-time"] = now
            self.datastore["selected-last"] = self.datastore["selected"]                        
            self.datastore["selected"] = None

        elif (self.datastore["status"] is 'Select'):
            if self.datastore["selected"] is not None:
                self.datastore["status"] = 'Run'
                self.datastore["status-time"] = now
            elif (len(self.datastore["reachable"]) == 0):
                self.datastore["status"] = 'FullTurn'
                self.datastore["status-time"] = now    

        elif (self.datastore["status"] is 'Run'):
            if self.datastore["self"] is not None and self.datastore["selected"] is not None:
                location = self.datastore["self"].location
                target = self.datastore["selected"].location

                s = vector.Vector(location)
                t = vector.Vector(target)
                dist = vector.norm(t) - vector.norm(s)
                print "Distance =", (int(dist)), '[', (int(location[0])), int(location[1]), int(location[2]), ']',

                if abs(int(dist)) < 50:
                    self.datastore["status"] = 'Reached'
                    self.datastore["status-time"] = now
                    self.datastore["explored"].append(self.datastore["selected"])

                elif self.datastore["interference"] is True:
                    self.datastore["status"] = 'Interference'
                    self.datastore["status-time"] = now

        elif self.datastore["status"] is 'Interference':
            if now - self.datastore["status-time"] > 1:
                self.datastore["status"] = 'Run'
                self.datastore["status-time"] = now
                self.datastore["interference"] = False

        elif self.datastore["status"] == 'FullTurn':            
            if self.datastore["selected"] is not None:
                print "Failed to reach", self.datastore["selected"].id
                self.datastore["selected-last"] = self.datastore["selected"]                        
                self.datastore["selected"] = None
                self.datastore["selected-time"] = now
            self.datastore["status"] = 'Select'
            self.datastore["status-time"] = now
            self.datastore["interference-once"] = False

        self.result = '2'

#Decide Behaviour
class DecideBehaviour(Behaviour):
    def setup(self):
        self.selected = None

    def action(self):
#        print "Decide"
        now = time.time()
        if self.datastore["status"] is 'Select':
            self.datastore["selected"] = self.selectTarget()
            if self.datastore["selected"] is not None:
                self.datastore["selected-time"] = now
                print "Selected : " ,self.datastore["selected"].id
#        else:
#            print "Target Location: ", self.datastore["selected"].location
#            print "Self Location: ", self.datastore["self"].location
#            print "Self Rotation: ", self.datastore["self"].rotation[0] * 2 * math.pi / 65535, self.datastore["self"].rotation[1] * 2 * math.pi / 65535, self.datastore["self"].rotation[2] * 2 * math.pi / 65535            
        self.result = '3'

    def selectTarget(self):
        self.selected = None
        i = len(self.datastore["new"])
        j = len(self.datastore["reachable"])
        if i != 0:
            i= random.randint(0,i-1)
            self.selected = self.datastore["new"][i]
        elif j != 0:
            j = random.randint(0,j-1)
            self.selected = self.datastore["reachable"][j]
#        if self.selected is not None:
#            print "Selected", self.selected.id, self.selected.reachable
        else:
            print "Can not select: Nothing Reachable!!!"
        return self.selected        

#Act behaviour
class ActBehaviour(Behaviour):
    def setup(self):
        self.socket = self.datastore["socket"]

    def action(self):
#        print "Act"
        if self.datastore["status"] == 'Select':
            pass
        elif self.datastore["status"] == 'Reached':
            print "\nExplored",
            for e in self.datastore["explored"]:
                print e.id,
        elif self.datastore["status"] is 'Run':
            self.selected = self.datastore["selected"]
            if self.selected is not None:
#                if self.datastore["status"] is 'Run':
#                    print "Run!!"
#                    msg = 'RunTo {Target '+self.selected.id+'}\r\n'
#                    self.socket.send(msg)
                if self.datastore["status"] is 'Run':
                    print "Run!!"
                    msg = 'RunTo {Location '+str(int(self.selected.location[0]))+' '+str(int(self.selected.location[1]))+' '+str(int(self.selected.location[2]))+'}\r\n'
                    self.socket.send(msg)
#                    print msg
        elif self.datastore["status"] is 'Interference':
            location = self.datastore["self"].location
            msg = 'Jump\r\n'
            i = random.randint(1,4)
            now = time.time()
            if i == 1:
                print "Move!!", i
                location[0] = location[0]+50
                location[1] = location[1]+50
                msg = 'RunTo {Location '+str(location[0])+' '+str(location[1])+' '+str(location[2])+'}\r\n'
            elif i == 2:
                print "Move!!", i
                location[0] = location[0]-50
                location[1] = location[1]+50
                msg = 'RunTo {Location '+str(location[0])+' '+str(location[1])+' '+str(location[2])+'}\r\n'
            elif i == 3:
                print "Move!!", i
                location[0] = location[0]+50
                location[1] = location[1]-50
                msg = 'RunTo {Location '+str(location[0])+' '+str(location[1])+' '+str(location[2])+'}\r\n'
            elif i == 4:
                print "Move!!", i
                location[0] = location[0]-50
                location[1] = location[1]-50
                msg = 'RunTo {Location '+str(location[0])+' '+str(location[1])+' '+str(location[2])+'}\r\n'
            self.socket.send(msg)
            self.sleep(0.5)
#            print msg
        elif self.datastore["status"] == 'FullTurn':            
            i = random.randint(2,4)
            msg = 'Rotate {Amount '+str(int(65536/i))+'}\r\n'
            self.socket.send(msg)
            print "\nfull turn and sleeping\n"
            self.sleep(0.5)
        self.result = '4'

#Connect Behaviour
class ConnectBehaviour(Behaviour):
    def setup(self):
        self.socket = self.datastore["socket"]
        self.msg = self.datastore["msg"]

    def action(self):
        print "Trying to connect to game"
        while self.datastore["connected"] == False:
            self.msg.parse()
            if len(self.datastore["observation"].events) > 0:
                for e in self.datastore["observation"].events:
                    if e.type == 'NFO':
                        msg = 'Init {name Bot1}\r\n'
                        self.socket.send(msg)
                        self.datastore["connected"] = True
        self.result = '0'

#Finite State Machine of FireTruck
class BotFSMBehaviour(FSMBehaviour):
    def setup(self):
        print "FSM setup"
        self.registerFirstState(ConnectBehaviour(datastore=self.datastore, name='connect'))
        self.registerState(ObserveBehaviour(datastore=self.datastore, name='observe'))
        self.registerState(OrientBehaviour(datastore=self.datastore, name='orient'))
        self.registerState(DecideBehaviour(datastore=self.datastore, name='decide'))
        self.registerState(ActBehaviour(datastore=self.datastore, name='act'))
        self.registerTransition('connect', 'observe', '0')
        self.registerTransition('observe', 'orient','1')
        self.registerTransition('orient', 'decide','2')
        self.registerTransition('decide', 'act','3')
        self.registerTransition('act', 'observe','4')
        self.registerDefaultTransition('connect', 'observe')
        self.registerDefaultTransition('observe', 'orient')
        self.registerDefaultTransition('orient', 'decide')
        self.registerDefaultTransition('decide', 'act')
        self.registerDefaultTransition('act', 'observe')

class Bot(Semant):
    def setup(self, socket, observation, message):
        self.__datastore = {}
        self.__datastore["socket"] = socket
        self.__datastore["observation"] = observation
        self.__datastore["msg"] = message
        self.__datastore["connected"] = False

        self.__datastore["visible"] = []
        self.__datastore["reachable"] = []
        self.__datastore["new"] = []
        self.__datastore["explored"] = []

        self.__datastore["self"] = None    
        self.__datastore["status"] = 'Select'
        self.__datastore["status-time"] = time.time()

        self.__datastore["selected"] = None    
        self.__datastore["selected-last"] = None
        self.__datastore["selected-time"] = time.time()

        self.__datastore["bumps"] = ['WAL','FAL','BMP']        
        self.__datastore["interference"] = False
        self.__datastore["interference-type"] = None
        self.__datastore["interference-time"] = time.time()
        self.__datastore["interference-once"] = False

        self.add_behaviour(BotFSMBehaviour(datastore=self.__datastore))

class HandleMessageBehaviour(Behaviour):
    def setup(self):
        self.socket = self.datastore["socket"] 
        self.msg = self.datastore["msg"]

    def action(self):
#        print "Receiving data"
        while(1):
            data = self.socket.recv(10000)
            if not data:
                break
#            print 'received', len(data), 'bytes'
#            print 'Received', repr(data)
            self.msg.appendToBuffer(data)
        self.datastore["msg"] = self.msg

class MessageHandler(Semant):
    def setup(self, socket, msg):
        self.__datastore = {}
        self.__datastore["socket"] = socket
        self.__datastore["msg"] = msg
        self.add_behaviour(HandleMessageBehaviour(datastore=self.__datastore))

class MyApp(App):
    def run(self, args):
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.settimeout(5)
        socket.connect((HOST, PORT))
        observation = UTObservation()
        message = UTMessage(observation)
        self.start_agent(MessageHandler, 'MSG_1', socket=socket, message=message)
        self.start_agent(Bot, 'Bot_1', socket=socket, observation=observation, message=message) 

if __name__ == "__main__":
    MyApp()

