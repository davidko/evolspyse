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

class StatusReceiveBehaviour(ReceiveBehaviour):
    def sort_func(self,x,y):
        return cmp(y[1],x[1])
    
    def handle_message(self, msg):
        # Overrides
        if msg.performative == ACLMessage.INFORM:
            self.agent.num_requests[msg.sender.shortname] = msg.content
        elif msg.performative == ACLMessage.REQUEST:
            reply = msg.create_reply(ACLMessage.INFORM)

            top_agents = self.agent.num_requests.items()
            top_agents.sort(self.sort_func)
            top_agents = top_agents[:50]
            reply.content = top_agents
            self.agent.send_message(reply)

class StatusAgent(Agent):
    def die(self):
        self.suspend()
        
    def setup(self):
        self.num_requests = {}
        self.add_behaviour(StatusReceiveBehaviour())
