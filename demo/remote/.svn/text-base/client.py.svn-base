#!/usr/bin/env python

"""scrappy's first Spyse encounter"""
__version__ = '0.2'

import time

from spyse.core.platform.hap import HAP
from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.content.content import ACLMessage
from spyse.app.app import App

class CivilianRequesterBehaviour(Behaviour):
    def setup(self, criers):
        self.__i = 0
        self.__criers = criers

    def action(self):
        msg = ACLMessage(ACLMessage.INFORM)
        msg.receivers.add(self.__criers[0])
        msg.content = self.__i
        self.__i += 1
        print "Sending a request"
        self.agent.send_message(msg)
        self.set_done()

class CivilianReceiverBehaviour(Behaviour):
    def action(self):
        print "Checking for response."
        msg = self.agent.get_message()
        if msg is None:
            print "I heard nothing."
            time.sleep(1)
            return
        item = msg.content
        if item is None:
            print "I heard something, but couldn't make it out."
            time.sleep(1)
            return
        if item == -1:
            print "That's all folks"
            self.agent.set_done()
            return
        print self.agent.name, "heard: ", item
        self.set_done()

class Civilian(Agent):
    def setup(self):
        print "I'm a civilian"
        hap = None
#        hap = HAP(host='turmeric', port='9000')
        aid = AID(shortname='Yelp', hap=hap)
        self.add_behaviour(CivilianRequesterBehaviour(criers=[aid]))
        self.add_behaviour(CivilianReceiverBehaviour())
        self.add_behaviour(CivilianRequesterBehaviour(criers=[aid]))
        self.add_behaviour(CivilianReceiverBehaviour())

class MyApp(App):
    def run(self, args):
        self.start_agent(Civilian)    

if __name__ == "__main__":
    MyApp()

