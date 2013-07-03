"""Spyse composite behaviour module"""

import time

from spyse.core.behaviours.behaviours import Behaviour


class CompositeBehaviour(Behaviour):
    def __init__(self, name='', **namedargs):
        self.__current = None
        self.__starting = True
        self.__behaviours = {}  # Sub-behaviours of this behaviour
        super(CompositeBehaviour, self).__init__(name, **namedargs)

    def add_behaviour(self, behaviour, name=None):
        # Override to use different data structures
        if name is not None:
            behaviour.name = self.name + '.' + name
        behaviour.agent = self.agent
        self.__behaviours[name] = behaviour

    def get_behaviours(self):
        # Override in subclasses to use different data structures
        return self.__behaviours.iter()

    def _set_agent(self, agent):
        # Overrides
        super(CompositeBehaviour, self)._set_agent(agent)
        for b in self.get_behaviours():
            b._set_agent(agent)

    def schedule_first(self):
        # Override in subclasses
        print 'schedule_first must be overriden'

    def schedule_next(self, current):
        # Override in subclasses
        print 'schedule_next must be overriden'

    def action(self):
        # Do not override; add sub-behaviours instead
        if self.__starting:
            self.__current = self.schedule_first()
            if self.__current is not None:
                self.__starting = False
        else:
            self.__current = self.schedule_next(self.__current)
        if self.__current is None:
            self.set_done()
        else:
            self.__current.action()


class ParallelBehaviour(CompositeBehaviour):
    """Perform a series of behaviours in "parallel" (actually, round robin)
       until all are finished.
    """
    def __init__(self, name='', **namedargs):
        super(ParallelBehaviour, self).__init__(name, **namedargs)
        self.__behaviours = []

    def add_behaviour(self, behaviour, name=None):
        if name is not None:
            behaviour.name = self.name + '.' + name
        self.__behaviours.append(behaviour)

    def get_behaviours(self):
        # Overrides
        return self.__behaviours

    def schedule_first(self):
        # Overrides
        if len(self.__behaviours)>0:
            return self.__behaviours[0]
        else:
            return None

    def schedule_next(self, current):
        # Overrides
        i = self.__behaviours.index(current)
        if current.done():
            self.__behaviours.remove(current)
            i -= 1
        # do the round robin dance now
        l = len(self.__behaviours)
        if l==0:
            return None
        else:
            next = self.__behaviours[(i+1) % l]
            return next


class SequentialBehaviour(CompositeBehaviour):
    """Performs a sequence of behaviours each waiting for the previous one to finish"""

    def __init__(self, name='', **namedargs):
        super(SequentialBehaviour, self).__init__(name, **namedargs)
        self.__behaviours = []

    def add_behaviour(self, behaviour, name=None):
        if name is not None:
            behaviour.name = self.name + '.' + name
        self.__behaviours.append(behaviour)
#        self.__behaviours.insert(0, behaviour)  # need a reversed list for popping

    def get_behaviours(self):
        # Overrides
        return self.__behaviours

    def __safe_pop(self, list):
        try:
            return list.pop(0)
#            return list.pop()
        except:
            return None

    def schedule_first(self):
        # Overrides
        return self.__safe_pop(self.__behaviours)

    def schedule_next(self, current):
        # Overrides
        if current.done():
            # the next behaviour of the sequence is scheduled
            return self.__safe_pop(self.__behaviours)
        else:
            return current

