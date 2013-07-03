#!/usr/bin/env python

"""
Spyse FSM demo

Agents are created and given finite state machine (FSM) behaviors
by means of the current and the legacy interface.

Using the current interface an FSM is built by registering a set of
transitions.  Each transition is defined by a pair of State objects
and a name.  The result of a state behaviour must be the name
(a string) of the transition that the machine should make out of
that state.

The FSM in this example consists of three states in a loop.
"""

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour, State
from spyse.app.app import App

class MyBehaviour(Behaviour):
    def setup(self, result_value):
        print "MyBehaviour", self.name, "setup"
        self.result_value = result_value

    def action(self):
        print "Agent", self.agent.name, "behaviour", self.name
        self.sleep(1)
        self.set_done()

    def _get_result(self):
        # Overrides
        if self.done():
            return self.result_value
        else:
            return None

class MyFSMBehaviour(FSMBehaviour):
    """This behaviour uses the new FSM interface"""
    def setup(self):
        print "MyFSMBehaviour setup"
        first_state = State(MyBehaviour(name='first', result_value='1'))
        second_state = State(MyBehaviour(name='second', result_value='2'))
        third_state = State(MyBehaviour(name='third', result_value='3'))
        self.add_transition(first_state, second_state, '1')
        self.add_transition(second_state, third_state, '2')
        self.add_transition(third_state, first_state, '3')
        self.first_state = first_state

class FSMAgent(Agent):
    def setup(self):
        self.add_behaviour(MyFSMBehaviour())

class MyApp(App):
    def run(self, args):
        self.start_agent(FSMAgent, 'Hopper')

if __name__ == "__main__":
    MyApp()

