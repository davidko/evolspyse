#!/usr/bin/env python

""" Token Pass
    
    TokenPasser agents will send a token to each other. This will happen in a 
    random way. If the Spyse platform is distributed one can see the token
    being sent from one system to another.
    
    If the application is started with 'token' as argument then a token (and 
    TokenPassers) will be created. If not only TokenPassers will be created
    and the token will have to be send from another instance of the application.
    
    Possible scenarios to start this demo:
    
    broadcast retrieve:
        Search for the agents at all other Spyse instances.
        token_pass.py --port=9001 --ns=start --distribution=broadcast-retrieve token
        token_pass.py --port=9002 --ns=local --distribution=broadcast-retrieve
        token_pass.py --port=9003 --ns=local --distribution=broadcast-retrieve
        etc
        
    broadcast update:
        Update all Spyse instances of newly created agents.
        token_pass.py --port=9001 --ns=start --distribution=broadcast-update token
        token_pass.py --port=9002 --ns=local --distribution=broadcast-update
        token_pass.py --port=9002 --ns=local --distribution=broadcast-update
        etc
        
    central:
        Let the first Spyse instance act as a server for other instances
        to register with.
        token_pass.py --port=9001 --ns=start --distribution=server token
        token_pass.py --port=9002 --ns=local --distribution=client
        token_pass.py --port=9003 --ns=local --distribution=client
        etc
"""
__version__ = '1.0'

import sys
import getopt

from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour, ReceiveBehaviour, SendBehaviour, TickerBehaviour
from spyse.core.content.content import ACLMessage
from spyse.app.app import App
from spyse.core.platform.df import Service
import time

import random 

class Token(object):
    """ The token has a name, a history of agents where it has been
        and a variable indicating the last agent it has visit """
    def __init__(self,name):
        self.name = name
        self.hist = []
        self.last = None
        
class RegisterServiceBehaviour(SendBehaviour):
    """ Register the service at the DF """
    def setup(self, args=None):
        self.performative= ACLMessage.REQUEST
        self.receivers = [ AID('DF') ]
        self.content = args # args = Service  
        
class SearchPasserServiceBehaviour(SendBehaviour):
    """ Search for the service at the DF """
    def setup(self, args=None):
        self.performative = ACLMessage.QUERY_REF
        self.receivers = [ AID('DF') ]
        self.content = args # args = Service

class PasserBehaviour(Behaviour):
    """ The PasserBehaviour can receive the Token from another Passer. Once it has
    recieved the token it adds itself to the Token history and will ask the DF to
    supply a list of all TokenPassers that are currently present. Upon receiving
    this list a random TokenPasser will be selected to send the Token to"""
    def setup(self,token=None):
        self.__service = Service('token-passing')

    def action(self):
        msg = self.agent.get_message()
        if msg:
            content = msg.content
            perf = msg.performative
            if perf == ACLMessage.INFORM:    # if we have received a list from the DF
                p = content[ random.randint(0, len(content)-1)]
                msg = ACLMessage(ACLMessage.INFORM_REF)
                msg.receivers.add(p)
                msg.content = self.agent.token
                self.agent.send_message(msg)
                self.agent.token=None
            elif perf == ACLMessage.INFORM_REF:    # if we have recieved the Token
                wait = 1
                if len(content.hist) % 10 == 0:
                    print 'Hop history:', content.hist
                print self.agent.shortname, 'received', content.name + '.', 'Waiting', wait, 'second.'
                print 'Hops so far:', len(content.hist)
                self.agent.token = content
                self.agent.token.hist.append(self.agent.aid)
                self.agent.token.last = self.agent.name
                time.sleep(wait)
                self.agent.add_behaviour(SearchPasserServiceBehaviour(args=self.__service))


class TokenPasser(Agent):
    """ The TokenPasser will register itself at the DF, create the token and look
        for other passers if needed and start the PasserBehaviour. """
    def setup(self,token=None):
        self.__datastore = {}
        s = Service('token-passing')

        self.add_behaviour(RegisterServiceBehaviour(args=s))        
        self.token = token
        if token is not None:
            self.token=token
            self.token.hist.append(self.aid)
            self.token.last = self.name
            self.add_behaviour(SearchPasserServiceBehaviour(args=s))
            print 'token set'

        self.add_behaviour(PasserBehaviour(token=self.token))
                

class MyApp(App):
    def run(self, args):   
        tokenname="Token-"+str(random.randint(0, 100))
        if len(args) >0 and args[0] == 'token':
            self.start_agent(TokenPasser,'Passer-'+str(random.randint(0, 10000)),token=Token(tokenname))
        else:
            self.start_agent(TokenPasser,'Passer-'+str(random.randint(0, 10000)))
        self.start_agent(TokenPasser,'Passer-'+str(random.randint(0, 10000)))
        self.start_agent(TokenPasser,'Passer-'+str(random.randint(0, 10000)))


if __name__ == "__main__":
    MyApp()

