#!/usr/bin/python

"""Spyse demo"""

import spyse
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour
from spyse.core.semant.semant import Semant
from spyse.app.app import App

import string
import socket
import time
from sets import Set
from Tkinter import *

HOST = 'localhost'
PORT = 3000

class UTEntity(object):
    def __init__(self, type, name, loc, reachable):
        self.type = type
        self.name = name
        self.location = loc
        self.reachable = reachable

class UnrealWorldModel(object):
    def __init__(self):
        self.entities = Set()

    def addEnt(self, type, rest):
        if type is 'NAV':
            i = string.find(rest, 'Id')+ 3
            j = string.find(rest, '}', i)
            name = rest[i:j]

            location = [0,0,0]
            i = string.find(rest, 'Location')+ 9
            k = string.find(rest, ',', i)
            l = string.find(rest, ',', k+1)
            j = string.find(rest, '}', l)
#            print i, j, k, l
            location[0] = string.atof(rest[i:k])
            location[1] = string.atof(rest[k+1:l])
            location[2] = string.atof(rest[l+1:j])

            i = string.find(rest, 'Reachable')+10
            j = string.find(rest, '}', i)
            reachable = rest[i:j]

#        print "Entity Added: ", type, name, location, reachable
            entity = UTEntity(type, name, location, reachable)
            self.entities.add(entity)

        if type is 'SLF': 
            location = [0,0,0]
            i = string.find(rest, 'Location')+ 9
            k = string.find(rest, ',', i)
            l = string.find(rest, ',', k+1)
            j = string.find(rest, '}', l)
#            print i, j, k, l
            location[0] = string.atof(rest[i:k])
            location[1] = string.atof(rest[k+1:l])
            location[2] = string.atof(rest[l+1:j])
            print "Self: Location ", location

    def clearEnt(self):
        self.entities = Set()

#Message parser
class UnrealMessage(object):
    def __init__(self, model):
        self.buffer = ''
        self.types = ['NFO', 'INV', 'NAV', 'VMS', 'SLF']
        self.model = model

    def parse(self):
        print "Parse"
        self.model.clearEnt()
        j = string.rfind(self.buffer, 'END')
        if j is -1:
            print "Parse failed"
            return
        i = string.rfind(self.buffer, 'BEG', 0, j)
        if i is -1:
            print "Parse failed"
            return

        for type in self.types:
            r = string.find(self.buffer, type, i, j)
            while r is not -1:
                s = string.find(self.buffer, '\n', r, j)
                if r is not -1:
                    cont = ''
                    r = r+4
                    while r < s:
                        cont = cont+self.buffer[r]
                        r = r+1
                    if type is 'NAV' or type is 'DOM' or type is 'MOV':
                        self.model.addEnt(type, cont)
                    if type is 'SLF':
                        self.model.addEnt(type, cont)

                r = string.find(self.buffer, type, s, j)
        self.buffer = self.buffer[j:]

    def appendToBuffer(self, data):
        self.buffer = self.buffer+data

#Observe behaviour
class ObserveBehaviour(Behaviour):
    def setup(self):
        self.socket = self.datastore["socket"]
        self.msg = self.datastore["msg"]

    def action(self):
#        print "Observe"
        try:
            data = self.socket.recv(1024)
            print 'Received', repr(data)        
            self.msg.appendToBuffer(data)
        except socket.timeout:
            print 'Nothing Received'
        self.datastore["msg"] = self.msg
        self.result = '1'

#Orient behaviour
class OrientBehaviour(Behaviour):
    def setup(self):
        self.msg = self.datastore["msg"]

    def action(self):
#        print "Orient"
        self.msg.parse()
        self.result = '2'

#Decide Behaviour
class DecideBehaviour(Behaviour):
    def setup(self):
        self.model = self.datastore["model"]
        self.selected = None

    def action(self):
#        print "Decide"
        if self.datastore["selected"] is None:
            self.selected = None
            for ent in self.model.entities:
                if ent.reachable == 'True':
                    if self.datastore["selected-last"] is not None:
                        print "Previous: ", self.datastore["selected-last"].name
                    if self.datastore["selected-last"] is None or ent.name != self.datastore["selected-last"].name:
                        self.selected = ent
#                        print "ENTITY SLECTED!!!!!!"
            if self.selected is not None:
                self.datastore["selected"] = self.selected
                self.datastore["selected-time"] = time.time()
                print "Selected : " ,self.datastore["selected"].name
        else:
            print "Target Location: ", self.datastore["selected"].location
            diff = time.time() - self.datastore["selected-time"]
            if diff > 10:
                self.datastore["selected-last"] = self.datastore["selected"]
                self.datastore["selected"] = None
#        print "Selected : " ,self.datastore["selected"].name
        self.result = '3'

#Act behaviour
class ActBehaviour(Behaviour):
    def setup(self):
        self.socket = self.datastore["socket"]

    def action(self):
#        print "Act"
        self.selected = self.datastore["selected"]

        if self.selected is not None:
            diff = time.time() - self.datastore["selected-time"]
#            if diff < 4:
#                msg = 'TurnTo {Target '+self.selected.name+'}\r\n'
#                self.socket.send(msg)
#            else:
            msg = 'RunTo {Target '+self.selected.name+'}\r\n'
            self.socket.send(msg)
#                print "Sending Msg: ", msg
        self.result = '4'

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

class ConnectBehaviour(Behaviour):
    def setup(self):
        self.connected = self.datastore["connected"]
        self.socket = self.datastore["socket"] 

    def action(self):
        if self.connected is False:
            print "No Connection!!!"
        else:
            self.datastore["host"] = self.socket.getsockname()    
            print "Connected to ", self.datastore["host"]

        if self.datastore["game"] is None:
            print "Trying to connect to game"
            data = self.socket.recv(1024)
            print 'Received', repr(data)
            if string.find(data,'NFO') is 0:
                msg = 'Init {name Bot1}\r\n'
                self.socket.send(msg)
                print "Sending Msg: ", msg
                try:
                    data = self.socket.recv(1024)
                    print 'Received', repr(data)        
                except socket.timeout:
                    print 'Nothing Received'
        else:
            print "Connection!!!"
        self.result = '0'

class Bot(Semant):
    def setup(self):
        self.__datastore = {}
        self.__datastore["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__datastore["socket"].settimeout(0.15)
        self.__datastore["socket"].connect((HOST, PORT))        
#        self.__datastore["socket"].setblocking(1)
        self.__datastore["connected"] = True        
        self.__datastore["host"] = None
        self.__datastore["game"] = None        
        self.__datastore["model"] = UnrealWorldModel()
        self.__datastore["msg"] = UnrealMessage(self.__datastore["model"])
        self.__datastore["selected"] = None    
        self.__datastore["selected-last"] = None    
        self.add_behaviour(BotFSMBehaviour(datastore=self.__datastore))

class MyApp(App):
    def run(self, args):
        self.start_agent(Bot, 'Bot_1')

if __name__ == "__main__":
    MyApp()

