#!/usr/bin/env python

"""Two agents playing Guess-the-number"""

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.fsm import FSMBehaviour
from spyse.app.app import App

"""
Riddler FSM:
    make riddle (choose random number)
    invite solvers to solve the riddle
    [wait for subscriptions?]
    wait for guesses
    if correct: reply to winner with accept, reply to all-winner with result, define new riddle
    if not correct: reply to solver with reject (more/less?)
    if timeout: inform all with cancel, define new riddle
Solver FSM:
    wait for invitation from riddler
    make a guess, send message to riddler
    wait for answer from riddler
    if correct: celebrate
    if not correct: make a new guess
    if timeout: give up
    if result: wait for new riddle
"""

### Riddler

# Keys for datastore
QUESTION = "question"
ANSWER = "answer"

# FSM event names
RIDDLE_MADE = "Initiation-sent"
SOLVED = "solved"
FAILED = "failed"

# FSM state names
AWAITING_GUESSES = "awaiting_guesses"


### Solver

# Keys for datastore
GUESSES = "quesses"

# FSM event names
RIDDLE_MADE = "Initiation-sent"

# FSM state names


from spyse.core.platform.df import Service
from spyse.core.agents.aid import AID
from spyse.core.agents.tkagent import TkinterAgent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour, SendBehaviour, ReceiveBehaviour
from spyse.core.behaviours.composite import SequentialBehaviour
from spyse.core.content.content import ACLMessage
from spyse.app.app import App

import time
from random import randint
#from sets import Set
#from Tkinter import *


class SearchServiceAgentsBehaviour(SendBehaviour):
    def setup(self, service):
        self.performative = ACLMessage.QUERY_REF
        self.receivers = [ AID('DF') ]
        self.content = service


class ReceiveServiceAgentsBehaviour(ReceiveBehaviour):

    def setup(self, datastore):
        self.datastore = datastore

    def handle_message(self, msg):
        # Overrides
        if msg.content is not None:
            perf = msg.performative
            if perf == ACLMessage.INFORM:
                self.datastore['providers'] = msg.content
        self.set_done()

class WaitForServiceAgentsBehaviour(TickerBehaviour):
    def setup(self, datastore):
        self.datastore = datastore

    def setService(self, service):
        self.__service = service

    def on_action(self):
        if (self.tick_count > 0) & (self.datastore['providers']!=[]):
            print "Providers found", self.datastore['providers']
            self.set_done()

    def on_tick(self):
        self.agent.add_behaviour(SearchServiceAgentsBehaviour(service=self.__service))
        self.agent.add_behaviour(ReceiveServiceAgentsBehaviour(datastore=self.datastore))

class SolverAgent(Agent):

    def setup(self):
        self.__datastore = {}
        self.add_behaviour(DummyBehaviour()) # just to keep the agent alive

    # Hook function for ContractNetInitiatorBehaviour
    def _select_proposal(self, proposals):
        min_price = None
        selected = None
        for proposal in proposals:
            price = proposal.content['price']
            print "Proposal selection", proposal.sender, price
            if (min_price is None) or (price<min_price):
                min_price = price
                selected = proposal
        if selected is not None:
            print "Selected", selected.sender, min_price
        else:
            print "Selected", selected, min_price
        return selected

    # Hook function for ContractNetInitiatorBehaviour
    def _process_result(self, result=None):
        content = result.content
        print "Got book with title", content['title'], "from", result.sender, "(" + content['signature'] + ")", "for", content['price']

    def _buy_book(self):
        self.__targetBookTitle = self.title_entry.get()
        #self.book_title.set("")
        self.title_entry.delete(0,END)
        print self.name, "buying book", self.__targetBookTitle

        sq = SequentialBehaviour()

        self.__datastore['providers'] = []
        ssab = WaitForServiceAgentsBehaviour(datastore=self.__datastore, period=5)
        service = Service('book-selling')
        ssab.setService(service)
        sq.add_behaviour(ssab, 'search-seller')

        call = {}
        call['title'] = self.__targetBookTitle
        self.__datastore['call'] = call
        sq.add_behaviour(ContractNetInitiatorBehaviour(
            datastore=self.__datastore,
            deadline=time.time() + 30,
            select_proposal=self._select_proposal,
            process_result=self._process_result
        ))

        self.add_behaviour(sq)

#===============================================================================
#    def create_widgets(self, frame):
#        frame.title(self.name + " - Buy a Book")
#
#        title_label = Label(frame)
#        title_label["text"] = "Title"
#        title_label.pack()
#
#        #self.book_title = StringVar()
#        #self.book_title.set("Multi-Agent Systems")    # this doesn't work, a bug in Tkinter?
#        self.title_entry = Entry(frame, width=20, background='white')#, textvariable=self.book_title)
#        self.title_entry.pack()
#
#        button1 = Button(frame, command=self.buy_book)
#        button1["text"]="Buy"
#        button1.pack()
#===============================================================================


class RegisterServiceBehaviour(SendBehaviour):
    def setup(self, service):
        self.performative = ACLMessage.REQUEST
        self.receivers = [ AID('DF') ]
        service = service
        self.content = service


class RiddlerBehaviour(FSMBehaviour):
    pass


class RiddlerAgent(Agent):
    def setup(self):
        self.datastore = {}
        self.__guesses = []
        service = Service('riddle')
        self.add_behaviour(RegisterServiceBehaviour(service=service))
        self.add_behaviour(RiddlerBehaviour(
            make_riddle=self._make_riddle,))
        
    def _make_riddle(self):
        # define question and answer
        self.datastore[QUESTION] = "I am thinking of a number between 0 and 100. Can you guess it?"
        self.datastore[ANSWER] = randint(100)
        
    def _check_guess(self, guess):
        if guess == self.datastore[ANSWER]:
            return SOLVED
        else:
            return FAILED

#===============================================================================
#    def create_widgets(self, frame):
#        frame.title(self.name + " - Sell a Book")
#        title_label = Label(frame)
#        title_label["text"]="Title"
#        title_label.pack()
#
#        self.book_title = Entry(frame, width=20, background='white')
#        self.book_title.pack()
#
#        price_label = Label(frame)
#        price_label["text"]="Price"
#        price_label.pack()
#
#        self.book_price = Entry(frame, width=20, background='white')
#        self.book_price.pack()
#
#        button1 = Button(frame, command=self.sell_book)
#        button1["text"]="Sell"
#        button1.pack()
#===============================================================================


class MyApp(App):
    def run(self, args):
        self.start_agent(RiddlerAgent, 'Joker')
        self.start_agent(RiddlerAgent, 'Mad_Hatter')
        self.start_agent(SolverAgent, 'Bruce_Wayne')
        self.start_agent(SolverAgent, 'Batman')
#        TkinterAgent.run_GUI()

if __name__ == "__main__":
    MyApp()
