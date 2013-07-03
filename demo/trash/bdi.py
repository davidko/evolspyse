"""Spyse BDI behaviour module"""

import time

from spyse.core.behaviours.behaviours import Behaviour


class Event(object):
    pass


class Option(object):
    pass


class BDIBehaviour(Behaviour):  # SequentialBehaviour ??? FSM ??? CompositeBehaviour ???

    __finished = False
    __event_queue = []
    __selected_events = []
    __plan_options = []
    __selected_plan_options = []

    def __init__(self, name='', **namedargs):
        self.get_new_external_events()
        super(BDIBehaviour, self).__init__(name, **namedargs)

    def action(self):
        self.__selected_events = self.eventSelector(self.__event_queue)
        self.__plan_options = self.optionGenerator(self.__selected_events)
        self.__selected_plan_options = self.deliberate(self.__plan_options)
        self.execute(self.__selected_plan_options)
        self.get_new_external_events()
        self.drop_successful_attitudes()
        self.drop_impossible_attitudes()

    def eventSelector(self, eventQueue=[]):
        events = []
        return events

    def optionGenerator(self, selectedEvents=[]):
        options = []
        return options

    def deliberate(self, plan_options=[]):
        options = []
        return options

    def execute(self, options=[]):
        pass

    def getNewExternalEvents(self):
        pass

    def dropSuccessfulAttitudes(self):
        pass

    def dropImpossibleAttitudes(self):
        pass

