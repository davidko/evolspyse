from spyse.core.behaviours.behaviours import Behaviour, SendBehaviour
from spyse.core.platform.df import Service
from spyse.core.content.content import ACLMessage
from spyse.core.agents.aid import AID

class DummyBehaviour(Behaviour):
    """ Do nothing, can be used for agents that don't do anything but need to be alive"""
    def setup(self):
        self.i = 0
        
    def action(self):
        self.i += 1

class RegisterServiceBehaviour(SendBehaviour):
    """ Register the service at the DF """
    def setup(self, args=None):
        self.performative= ACLMessage.REQUEST
        self.receivers = [AID('DF')]
        self.content = args # args = Service 
        
class SearchServiceBehaviour(SendBehaviour):
    """ Search for the service at the DF """
    def setup(self, args=None):
        self.performative = ACLMessage.QUERY_REF
        self.receivers = [AID('DF')]
        self.content = args # args = Service