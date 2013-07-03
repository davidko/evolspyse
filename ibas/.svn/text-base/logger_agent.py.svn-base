from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour, ReceiveBehaviour
from spyse.core.protocols.request import RequestParticipantBehaviour
from spyse.core.protocols import request
from spyse.core.content.content import ACLMessage
from spyse.core.agents.aid import AID

import Pyro.core
import time
from xml.dom import minidom
from random import randint
from datetime import datetime, timedelta

class LoggerReceiveBehaviour(ReceiveBehaviour):

    def handle_message(self, msg):
        # Overrides
        if msg.performative == ACLMessage.INFORM:
            self.agent.messages.append(msg.sender.shortname+"#"+msg.content)
        elif msg.performative == ACLMessage.REQUEST:
            reply = ACLMessage(ACLMessage.INFORM)
            reply.receivers.add(msg.sender)
            reply.content = self.agent.messages
            self.agent.send_message(reply)

class LoggerAgent(Agent):
    #def die(self):
    #    self.suspend()
        
    def setup(self):
        self.messages = []
        self.add_behaviour(LoggerReceiveBehaviour())
