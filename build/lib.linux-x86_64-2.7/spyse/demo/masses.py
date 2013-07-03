#!/usr/bin/env python

"""
Spyse masses demo

Starts the number of agents (default: 20) specified on the command line,
assigning to them dummy waiting behaviours.

The purpose of the demo is to test the Spyse platform's ability to run
massive numbers of agents.
"""

from random import randint

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import TickerBehaviour
from spyse.app.app import App

class DummyBehaviour(TickerBehaviour):
    def on_tick(self):
        self.period = randint(3, 10)
        print self.agent.name, "tick count:", self.tick_count

class DummyAgent(Agent):
    def setup(self):
        self.add_behaviour(DummyBehaviour())

class MyApp(App):
    def run(self, args):
        n = 20
        if not args is None and len(args)>0:
            n = int(args[0])
        print "Starting a mass of", n, "agents each of which increments its counter at random intervals."
        for a in range(n):
            self.start_agent(DummyAgent, 'Agent_' + str(a).zfill(4))

if __name__ == "__main__":
    MyApp()

