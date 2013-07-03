#!/usr/bin/env python

"""
Demo of StepperBehaviours

Spyse agents can either be round-robin scheduled or threaded.

If they are round-robin scheduled then the scheduling is predictable---
each agent completes one action per "step"---but CPU time may be
unfairly distributed.

If they are threads then they receive roughly equal shares of CPU time
but the precise distribution depends on the OS, on current load, etc.,
and is thus unpredictable.

StepperBehaviour was created in order to allow threaded agents of a
certain class to behave like r-r scheduled agents.  It is EXPERIMENTAL
and may be removed in the future if we find a better technique.
"""

from random import randint
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import StepperBehaviour
from spyse.app.app import App

# Define a custom behaviour class
class HelloBehaviour(StepperBehaviour):
    # Customize a StepperBehaviour by overriding do_step
    def do_step(self):
        # Mark this behaviour as finished so that it will be removed
        # from the agent's behaviour list.
        super(HelloBehaviour, self).do_step()
        if randint(0, 99) < 25:
            self.set_step_done()

# Define a custom agent class
class HelloAgent(Agent):
    # Customize the Agent class by overriding setup()
    def setup(self):
        # Add the custom behaviour for the agent to perform.
        # An agent will die as soon as all its behaviours are complete.
        self.add_behaviour(HelloBehaviour())

# Define a custom application class
class MyApp(App):
    # Overrides
    def run(self, args):
        self.start_agent(HelloAgent, "Red")
        self.start_agent(HelloAgent, "Hot")
        self.start_agent(HelloAgent, "Che")

# Instantiate and run MyApp
if __name__ == "__main__":
    MyApp()
