#!/usr/bin/env python

"""
Spyse demonstration of the ContractNet protocol, modelled after the JADE bookTrading demo

When run, the demo starts three agents: a buyer and two sellers.  The buyer expresses a wish to purchase a book and the sellers make offers to sell that book at quoted prices.

To use, start the program and then enter "MAS" into the buyer's "Title" box.

To exit, press control-C.  FIXME: currently on GNU the app must be killed.
"""

from spyse.core.platform.df import Service
from spyse.core.agents.aid import AID
from spyse.core.agents.tkagent import TkinterAgent
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour, SendBehaviour, ReceiveBehaviour
from spyse.core.behaviours.composite import SequentialBehaviour
from spyse.core.content.content import ACLMessage
from spyse.core.protocols.contractnet import ContractNetInitiatorBehaviour, ContractNetParticipantBehaviour
from spyse.app.app import App

import time
import random
from sets import Set
from Tkinter import *

class DummyBehaviour(Behaviour):
    def setup(self):
        self.i = 0

    def action(self):
        self.i += 1

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
        content = msg.content
        if content is not None:
            perf = msg.performative
            if perf == ACLMessage.INFORM:
                self.datastore['providers'] = content
        self.set_done()

class SearchSellerAgentsBehaviour(TickerBehaviour):
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

class BookBuyerAgent(TkinterAgent):

    __targetBookTitle = "Lolita"
    __sellerAgents = Set()

    def setup(self):
        self.__books = Set()
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
            print "Selected seller", selected.sender, "at price", min_price
        else:
            print "Selected none"
        return selected

    # Hook function for ContractNetInitiatorBehaviour
    def _process_result(self, result=None):
        content = result.content
        print "Got book with title", content['title'], "from", result.sender, "(" + content['signature'] + ")", "for", content['price'], "monetary units"

    def buy_book(self):
        self.__targetBookTitle = self.title_entry.get()
        #self.book_title.set("")
        self.title_entry.delete(0,END)
        print self.name, "buying book", self.__targetBookTitle

        sq = SequentialBehaviour()

        self.__datastore['providers'] = []
        ssab = SearchSellerAgentsBehaviour(datastore=self.__datastore, period=5)
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

    def create_widgets(self, frame):
        frame.title(self.shortname + " - Buy a Book")

        title_label = Label(frame)
        title_label["text"] = "Title"
        title_label.grid(row=0, column=0, padx=5, pady=5)
#        title_label.pack()

        #self.book_title = StringVar()
        #self.book_title.set("Multi-Agent Systems")    # this doesn't work, a bug in Tkinter?
        self.title_entry = Entry(frame, width=40, background='white')#, textvariable=self.book_title)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
#        self.title_entry.pack()

        button1 = Button(frame, command=self.buy_book)
        button1["text"]="Buy"
        button1.grid(row=0, column=2, padx=5, pady=5)
#        button1.pack()

class RegisterServiceBehaviour(SendBehaviour):
    def setup(self, service):
        self.performative = ACLMessage.REQUEST
        self.receivers = [ AID('DF') ]
        service = service
        self.content = service

class BookSellerAgent(TkinterAgent):
    def setup(self):
        self.__library = {}
        self.__library['MAS'] = random.randint(50, 150)
        service = Service('book-selling')
        self.add_behaviour(RegisterServiceBehaviour(service=service))
        self.add_behaviour(ContractNetParticipantBehaviour(
            make_proposal=self._make_proposal,
            execute_contract=self._execute_contract
        ))

    # Hook function for ContractNetParticipantBehaviour
    def _make_proposal(self, call):
        content = call.content
        print self.name, "making proposal with content", content
        title = content['title']

        if title == "NoWay":
            proposal = call.create_reply()
            proposal.performative = ACLMessage.REFUSE
            return proposal

        print self.name, "making proposal with content", content, "and call", call

        try:
            price = self.__library[title]
            print self.name, 'making proposal', title, "at price", price
            content['price'] = price
            content['signature'] = self.name
            proposal = call.create_reply()
            proposal.performative = ACLMessage.PROPOSE
            print self.name, "making proposal with content", content
            proposal.content = content
            return proposal
        except:
            return None

    # Hook function for ContractNetParticipantBehaviour
    def _execute_contract(self, conclusion):
        # None ==> no answer yet
        # False ==> Failure
        # True ==> Inform-Done
        # Other ==> Inform-Result
        result = conclusion.content
        return result

    def sell_book(self):
        self.__library[self.book_title.get()] = int(self.book_price.get())
        self.book_title.delete(0,END)
        self.book_price.delete(0,END)
        print self.name, "selling book", self.__library

    def create_widgets(self, frame):
        frame.title(self.shortname + " - Sell a Book")
        
        title_label = Label(frame)
        title_label.grid(row=0, column=0, padx=5, pady=5)
        title_label["text"]="Title"
#        title_label.pack(padx=5, pady=5)
        
        self.book_title = Entry(frame, width=40, background='white')
        self.book_title.grid(row=0, column=1, padx=5, pady=5)
#        self.book_title.pack(padx=5, pady=5)
        
        price_label = Label(frame)
        price_label.grid(row=1, column=0, padx=5, pady=5)
        price_label["text"]="Price"
#        price_label.pack(padx=5, pady=5)
        
        self.book_price = Entry(frame, width=40, background='white')
        self.book_price.grid(row=1, column=1, padx=5, pady=5)
#        self.book_price.pack(padx=5, pady=5)
        
        button1 = Button(frame, command=self.sell_book)
        button1.grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        button1["text"]="Sell"
#        button1.pack(padx=5, pady=5)

class MyApp(App):
    def run(self, args):
        self.create_agent(BookSellerAgent, 'Bookseller A')
        self.create_agent(BookSellerAgent, 'Bookseller B')
        self.create_agent(BookBuyerAgent, 'Book buyer')
        self.invoke_all_agents()
        TkinterAgent.run_GUI()

if __name__ == "__main__":
    MyApp()

