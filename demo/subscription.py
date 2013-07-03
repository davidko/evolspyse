#!/usr/bin/env python

"""
Spyse subscription demo

Illustrates one agent subscribing to another's publications.
"""

from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.protocols.subscription import SubscriptionInitiatorBehaviour, SubscriptionParticipantBehaviour
from spyse.app.app import App

from random import randint
import time


class PublisherAgent(Agent):
    def setup(self, maximum):
        self.__count = 1
        self.__maximum = maximum
        self.add_behaviour(SubscriptionParticipantBehaviour(
            send_response=self._send_response,
            send_notifications=self._send_notifications,
            cancel=self._cancel,
            check_updates=self._check_updates
        ))

    def _send_notifications(self):
        notification = randint(0,99)
        if self.__count > self.__maximum:
            print "\nAgent", self.name, "ceasing publication."
            self.die()
        else:
            print "\nAgent", self.name, "sending  notification", self.__count, "/", self.__maximum, "with info:", notification
            self.__count += 1
        return notification

    def _send_response(self):
        print "Agent", self.name, "sending response"

    def _cancel(self):
        print "Agent", self.name, "cancelling client's subscription"

    def _check_updates(self):
        if randint(0,9) >= 1:
            return False
        return True


class SubscriberAgent(Agent):
    def setup(self, subscription, maximum):
        self.__count = 1
        self.__maximum = maximum
        self.add_behaviour(SubscriptionInitiatorBehaviour(
            subscription=subscription,
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform,
            handle_failure=self._handle_failure,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))

    def _handle_response(self):
        print "Agent", self.name, "handling response"

    def _handle_agree(self):
        print "Agent", self.name, "handling agreement"

    def _handle_refuse(self):
        print "Agent", self.name, "handling refusal"

    def _handle_inform(self, content):
        self.__count += 1
        print "Agent", self.name, "handling notification", self.__count, "/", self.__maximum, "with info:", content

    def _handle_failure(self):
        print "Agent", self.name, "handling failure"

    def _cancel(self):
        print "Agent", self.name, "cancelling its subscription"

    def _check_cancel(self):
        if self.__maximum and self.__count >= self.__maximum:
            print "Agent", self.name, "signalling cancel"
            return True
        return False


class MyApp(App):
    def run(self, args):
        self.start_agent(PublisherAgent, 'Pub', maximum=40)  # To reveal bug, arrange it so that publisher ends earlier than subscribers
        time.sleep(0.2)
        subscription=AID('Pub')
        self.start_agent(SubscriberAgent, 'Red', subscription=subscription, maximum=13)
        time.sleep(0.2)
        self.start_agent(SubscriberAgent, 'Hot', subscription=subscription, maximum=17)
        time.sleep(0.2)
        self.start_agent(SubscriberAgent, 'Che', subscription=subscription, maximum=30)

if __name__ == "__main__":
    MyApp()
