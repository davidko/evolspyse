#!/usr/bin/env python

"""
Spyse demo of sequential and parallel behaviours

An agent is created with two behaviours, the first of which is
a sequential behavior consisting of three behaviours, the second
of which is a parallel behaviour itself consisting of three
behaviours.
"""

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.composite import SequentialBehaviour, ParallelBehaviour
from spyse.app.app import App

import random

class SimpleTaskBehaviour(Behaviour):
    def action(self):
        print "Behaviour", self.name, "is active"
        # Pretend we're doing something that takes 100-1000 ms
        self.sleep(random.randint(100, 1000) / 1000.0)
        # Are we finished?
        r = random.randrange(100)
        if r<20:
            self.set_done()
            print "Behaviour", self.name, "is now complete."

class WorkflowAgent(Agent):
    def setup(self):
        seq_b = SequentialBehaviour()
        self.add_behaviour(seq_b, 'b0')
        self.add_behaviour(SimpleTaskBehaviour(), 'b1')

        seq_b.add_behaviour(SimpleTaskBehaviour(), 's0')

        par_b = ParallelBehaviour()
        seq_b.add_behaviour(par_b, 's1')

        par_b.add_behaviour(SimpleTaskBehaviour(), 'p0')
        par_b.add_behaviour(SimpleTaskBehaviour(), 'p1')
        par_b.add_behaviour(SimpleTaskBehaviour(), 'p2')

        seq_b.add_behaviour(SimpleTaskBehaviour(), 's2')

class MyApp(App):
    def run(self, args):
        self.start_agent(WorkflowAgent, 'workforce')

if __name__ == "__main__":
    MyApp()
