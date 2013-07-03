#!/usr/bin/env python

"""scrappy's first Spyse encounter"""
__version__ = '0.2'

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.content.content import ACLMessage
from spyse.app.app import App

import random

class CrierReceiverBehaviour(Behaviour):
    def setup(self):
        pass

    def action(self):
        msg = self.agent.get_message()
        if msg is None:
            return
        item = msg.content
        if item is None:
            return
        print "Received a cry request"
        reply = ACLMessage(ACLMessage.INFORM)
        reply.receivers.add(msg.sender)
        reply.content = self.agent.cry(item)
        self.agent.send_message(reply)

class TownCrier(Agent):
    def setup(self):
        self.add_behaviour(CrierReceiverBehaviour())
        self.__messages = ["Hear ye Hear ye!","I said HEAR as in come and listen!","Gather around me please!",
                         "Have ye heard teh news today!","Spyse wizards are coming to town!"]

    def cry(self, i):
        i = int(i)
        if i < len(self.__messages):
            return self.__messages[i]
        else:
            return -1;

class DummyBehaviour(Behaviour):
    def setup(self):
        self.i = 0
    def action(self):
        self.i += 1

class MyApp(App):
    def run(self, args):
        self.start_agent(TownCrier, 'Yelp')

if __name__ == "__main__":
    MyApp()

