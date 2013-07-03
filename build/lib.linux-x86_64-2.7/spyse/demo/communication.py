#!/usr/bin/env python

"""
Spyse communication demo

Sprek and Perle are senders.  They send a numbered messages to
receivers Cooter and Lester.
"""

from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.content.content import ACLMessage
from spyse.app.app import App

import random

class SenderBehaviour(Behaviour):
    def setup(self, iterations):
        self.__iterations = iterations

    def action(self):
        msg = ACLMessage(ACLMessage.INFORM)
        msg.receivers.add(AID('Cooter'))
        msg.receivers.add(AID('Lester'))
        msg.receivers.add(AID('Snoopy'))
        if self.__iterations > 0:
            content = self.agent.name + "/" + str(self.__iterations)
            print 'Agent', self.agent.name, "sending message", self.__iterations
        else:
            content = None
        msg.content = content
        self.agent.send_message(msg)
        if self.__iterations > 0:
            self.__iterations -= 1
            # Pretend we're doing something that takes 10-100 ms
            self.sleep(random.randint(10, 100) / 1000.0)
        else:
            self.set_done()

class SenderAgent(Agent):
    def setup(self):
        self.add_behaviour(SenderBehaviour(iterations=20))

class ReceiverBehaviour(Behaviour):
    def setup(self):
        pass

    def action(self):
        msg = self.agent.get_message()
        if msg:
            item = msg.content
            if item is None:
                print 'Agent', self.agent.name, "is done."
                self.set_done()
            else:
                print 'Agent', self.agent.name, "reading message", item
                # Pretend we're doing something that takes 10-100 ms
                self.sleep(random.randint(10, 100) / 1000.0)

class ReceiverAgent(Agent):
    def setup(self):
        self.add_behaviour(ReceiverBehaviour())

class MyApp(App):
    def run(self, args):
        self.start_agent(ReceiverAgent, 'Cooter')
        self.start_agent(ReceiverAgent, 'Lester')
        self.start_agent(ReceiverAgent, 'Snoopy')
        self.start_agent(SenderAgent, 'Perle')
        self.start_agent(SenderAgent, 'Sprek')

if __name__ == "__main__":
    MyApp()

