"""Spyse finite state machine behaviour module"""

import time

from spyse.core.behaviours.composite import Behaviour, CompositeBehaviour


class State(object):
    """A state in a finite state machine

       Instance attribute "behaviour" is the behaviour that runs when
       the machine is in that state; the result of this behaviour
       determines which state to schedule next.

       One possible way of modifying the FSM is to replace this
       behaviour with another one.

       Instance attribute "transitions" is the dictionary that maps
       transition name to next state.
    """
    def __init__(self, behaviour=None):
        if behaviour is None:
            self.behaviour = Behaviour()
        else:
            self.behaviour = behaviour
        self.transitions = {}

    def add_transition(self, state, event_name):
        self.transitions[event_name] = state

    # The name and action of this state are those of its behaviour.
    # This may change in the future.

    def __get_name(self):
        return self.behaviour.name

    name = property(__get_name, None, None, "name of this state")

    def action(self):
        return self.behaviour.action()


class FSMBehaviour(CompositeBehaviour):

    __DEFAULT_EVENT_NAME = ''

    def __init__(self, name='', **namedargs):
        self._states = set()  # Warning: may not include self.first_state
        self.first_state = None
        super(FSMBehaviour, self).__init__(name, **namedargs)

    def get_behaviours(self):
        # Overrides
        behaviours = []
        self._states.add(self.first_state)  # Handle the odd case where there are no transitions to or from first_state
        for state in self._states:
            if state is not None:
                behaviours.append(state.behaviour)
        return behaviours

    def schedule_first(self):
        return self.first_state

    def schedule_next(self, current):
        if current is None:
            return None
        event_name = current.behaviour.result
        if event_name is None:
            return None
        try:
            target = current.transitions[event_name]
        except KeyError:
            try:
                target = current.transitions[self.__DEFAULT_EVENT_NAME]
            except KeyError:
                return None
        if target is None:
            self.set_done()
        return target

    def _add_state(self, state):
        if state is not None:
            self._states.add(state)

    def add_transition(self, pre, post, event_name=None):
        if event_name is None:
            event_name = self.__DEFAULT_EVENT_NAME
        self._add_state(pre)
        self._add_state(post)
        pre.add_transition(post, event_name)

