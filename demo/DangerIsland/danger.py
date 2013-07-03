#!/usr/bin/env python

from spyse.app.app import App
import spyse.asw.environment
from spyse.demo.DangerIsland.danger_env import DI_Environment
from spyse.core.agents.wxagent import wxAgent
from spyse.demo.DangerIsland.danger_gui import DI_GameAgent
from spyse.asw.asw_gui import wxGameAgent

from spyse.core.platform.platform import Platform
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour
from random import randint

from spyse.util.trig import *

import os
import sys
import math
import time
import random
import threading
from datetime import datetime


#---------------------------------------------------------------------------------
# Robot Agent

class Robot(Agent):
    def setup(self, env, location, rotation, speed):
        self.env = env
        self.env.place(self.name, label=self.__class__.__name__, location=location, rotation=rotation, speed=speed)
        self.add_behaviour(RobotBehaviour(period=2, env=self.env))

class RobotBehaviour(TickerBehaviour):
    def setup(self, env):
        print "RobotBehaviour.setup"
        self.env = env
        self.roadmap = self.env.read('Roadmap')
#        self.da = 12
        self.last_sensor = None
        self.current_road = None # ('Node_00', 'Node_01') # TODO: = None
        
    def on_tick(self):
        print datetime.now()
        self.body = self.env.read(self.agent.name)
        self.x, self.y = self.body['location']
        nodes = self.roadmap['nodes']
        delta = 10
        
        # if close to end of road segment
#        if self.current_road is not None: print self.env.distance(self.agent.name, nodes[self.current_road[1]])
        if self.current_road is None or self.env.distance(self.agent.name, nodes[self.current_road[1]]) < delta:
            print "checking"
            # look for the closest next destination of a road segment in current direction
            current_origin, current_destination = self.current_road if self.current_road is not None else (None, None)
            roads = self.env.on_road(self.agent.name)
            print roads
            print current_origin, current_destination
            
            # select next road segment to travel
            next_roads = []
            return_road = None
            for r in roads:
#                print ">>> 0"
                # road that returns to origin of current segment
                if r[1] == current_origin:
                    print ">>> 1"
                    return_road = r
                # roads originating from current destination
                elif r[0] == current_destination or current_destination is None:
                    print ">>> 2"
                    next_roads.append(r)
                    
            nr_options = len(next_roads)
            print "nr_options", nr_options
            # if no adjacent road found, try to return
            if nr_options == 0:
                print ">>> 3"
                self.current_road = return_road
            # if exactly one adjacent road found, take that one
            elif nr_options == 1:
                print ">>> 4"
                self.current_road = next_roads[0]
            # if multiple adjacent roads found, consult a sensor,
            # otherwise choose best match with current direction
            elif nr_options > 1:
                print ">>> 5"
                self.current_road = self.check_sensors()
                if self.current_road is None:
                    self.current_road = random.choice(next_roads)
            # otherwise, move on and try finding roads later on
            else:
                print ">>> 6"
                self.current_road = None
            
            if self.current_road is not None:
                dx = nodes[self.current_road[1]][0]-self.x
                dy = nodes[self.current_road[1]][1]-self.y
    
                if (dx != 0.0 and dy != 0.0):
                    rot = rad2deg(math.atan2(dy, dx)) - self.body['rotation']
                    self.env.turn(self.agent.name, rot)
                
    def check_sensors(self):
        # check whether a sensor is close that has not been used, yet
        sensors = self.env.neighbours(self.agent.name, label='sensor')
        print "sensors", len(sensors)
        if len(sensors) > 0:
            s = sensors[0]
#            print s
            if s['name'] is not self.last_sensor:
                sx, sy = s['location']
                dx = sx - self.x
                dy = sy - self.y
#                print (dx, dy), math.sqrt(dx*dx + dy*dy)
                if math.sqrt(dx*dx + dy*dy) < 10:
                    self.last_sensor = s['name']
                    return self.roadmap['edges'][s['direction']]
                else:
                    return None
            else:
                return None
        else:
            return None
#                    print s['direction']-self.body['rotation']
#                    self.env.turn(self.agent.name, s['direction']-self.body['rotation'])

    def find_neighbours(self):
        # sense environment and select road cells
        cells = self.env.neighbours(self.agent.name, label='cell')
#        print len(cells)
        roads = [i for i in cells if i['type'] == 'road']
        print "roads", len(roads)
        rot = self.follow_roads(roads)
        self.env.turn(self.agent.name, rot)

#        self.env.turn(self.agent.name, random.randint(-self.da, self.da))

    def follow_roads(self, roads):
        d = []
        for r in roads:
            dx = r['location'][0]-self.body['location'][0]
            dy = r['location'][1]-self.body['location'][1]

            if (dx == 0.0 and dy == 0.0):
                d.append(0.0)
            else:
                a = rad2deg(math.atan2(dy, dx)) - self.body['rotation']
                d.append((abs(a), a))

        if len(d)>0:
            return min(d)[1]
        else:
            return 0.0


#---------------------------------------------------------------------------------
# Application

class MyContainer(App):
    def run(self, args):
        print "MyContainer run"
        width = 1200
        height = 900
        env = DI_Environment(condition=Platform.is_running, x_min=0, x_max=width, y_min=0, y_max=height)
        env.start()
#        contr=env.controller
        self.start_agent(Robot, "Robot_0", env=env.controller, location=(522,  99), rotation= 125, speed=3)
        self.start_agent(Robot, "Robot_1", env=env.controller, location=(296, 399), rotation=  60, speed=4)
        self.start_agent(Robot, "Robot_2", env=env.controller, location=(705, 394), rotation= 215, speed=3)
        self.start_agent(DI_GameAgent, 'Viewer', env=env.controller, size=(width, height))
        wxAgent.run_GUI()

if __name__ == "__main__":
    MyContainer()
