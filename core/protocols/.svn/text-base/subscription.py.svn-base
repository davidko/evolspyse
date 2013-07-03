"""Spyse FIPA subscription protocol module"""

# FIPA Subscribe Interaction Protocol
# http://www.fipa.org/specs/fipa00035/SC00035H.html
#
# Note: the subscriber is the "initiator" and the publisher is
# the "participant" in FIPA terminology.

import time
from datetime import datetime
from random import randint
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour, State
from spyse.core.content.content import ACLMessage

# Keys for datastore
message_key = "message_key"
subscription_key = "subscription_key"  # publisher key
subscribers_key = "subscribers_key"
default_key = "default_key"

# FSM event names
INITIATION_SENT = "INITIATION_SENT"
RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
AGREE_RECEIVED = "AGREE_RECEIVED"
REFUSE_RECEIVED = "REFUSE_RECEIVED"
INFORM_RECEIVED = "INFORM_RECEIVED"
FAILURE_RECEIVED = "FAILURE_RECEIVED"
AGREE_HANDLED = "AGREE_HANDLED"
REFUSE_HANDLED = "REFUSE_HANDLED"
INFORM_HANDLED = "INFORM_HANDLED"
FAILURE_HANDLED = "FAILURE_HANDLED"
RESPONSE_HANDLED = "RESPONSE_HANDLED"
CANCEL_SIGNALLED = "CANCEL_SIGNALLED"
CANCEL_REQUESTED = "CANCEL_REQUESTED"
CANCEL_SUCCEEDED = "CANCEL_SUCCEEDED"
CANCEL_FAILED = "CANCEL_FAILED"
CANCELLED = "CANCELLED"
FINISHED = "FINISHED"
#
INITIATION_RECEIVED = "INITIATION_RECEIVED"
RESPONSE_SENT = "RESPONSE_SENT"
UPDATED = "UPDATED"
NOT_UPDATED = "NOT_UPDATED"
NOTIFIED = "NOTIFIED"


class StateBehaviour(Behaviour):
    """Behaviour in a subscription finite state machine state.

       Includes reference to a common data store needed by
       behaviours in multiple FSM states.

       Includes check_cancel callback so that cancellation
       can be requested by initiator at any point in the 
       protocol sequence.
    """
    def __init__(self, name='', datastore=None, **namedargs):
        self.datastore = datastore
        super(StateBehaviour, self).__init__(name, **namedargs)


##################################################################
# Subscription participant (i.e., publisher) behaviours
##################################################################


class AwaitInitiationBehaviour(StateBehaviour):
    def action(self):

        if message_key in self.datastore:
            self.result = default_key
        else:
            msg = self.agent.get_message()
            if msg is None:
                self.result = default_key
            else:
                self.datastore[message_key] = msg
                if msg.performative == ACLMessage.CANCEL:
                    self.result = CANCEL_REQUESTED
                else:
                    subscribers = self.datastore[subscribers_key]
                    subscribers.append(msg.sender)
                    self.result = INITIATION_RECEIVED


class SendResponseBehaviour(StateBehaviour):
    def __init__(self, name='', send_response=None, **namedargs):
        if send_response is not None:
            self.send_response = send_response
        super(SendResponseBehaviour, self).__init__(name, **namedargs)

    def action(self):
        self.send_response()
        if message_key in self.datastore:
            msg = self.datastore[message_key]
            reply = msg.create_reply(ACLMessage.AGREE)
            self.agent.send_message(reply)
            del self.datastore[message_key]
            self.result = RESPONSE_SENT
        else:
            self.result = default_key


class CheckUpdatesBehaviour(StateBehaviour):
    def __init__(self, name='', check_updates=None, **namedargs):
        if check_updates is not None:
            self.check_updates = check_updates
        super(CheckUpdatesBehaviour, self).__init__(name, **namedargs)

    def action(self):
        # randomize result, need to find a mechanism for detecting changes
        if self.check_updates():
            self.result = UPDATED
        else:
            self.result = NOT_UPDATED
 

class SendNotificationBehaviour(StateBehaviour):
    def __init__(self, name='', send_notifications=None, **namedargs):
        if send_notifications is not None:
            self.send_notifications = send_notifications
        super(SendNotificationBehaviour, self).__init__(name, **namedargs)

    def action(self):
        notification = self.send_notifications()
        msg = ACLMessage(ACLMessage.INFORM)
        for subscriber in self.datastore[subscribers_key]:
            msg.receivers.add(subscriber)
        msg.content = notification
        self.agent.send_message(msg)
        self.result = NOTIFIED


class ProcessCancelBehaviour(StateBehaviour):
    def __init__(self, name='', cancel=None, **namedargs):
        if cancel is not None:
            self.cancel = cancel
        super(ProcessCancelBehaviour, self).__init__(name, **namedargs)

    def action(self):
        self.cancel()
        if message_key in self.datastore:
            msg = self.datastore[message_key]
            reply = msg.create_reply(ACLMessage.INFORM_DONE)
            self.agent.send_message(reply)
            del self.datastore[message_key]
            subscribers = self.datastore[subscribers_key]
            for subscriber in subscribers:
                if subscriber == msg.sender:  # AIDs
                    subscribers.remove(subscriber)
            self.result = CANCELLED
        else:
            self.result = default_key


class SubscriptionParticipantBehaviour(FSMBehaviour):
    """Behaviour for publisher role"""

    def __init__(self, name='', datastore=None, send_response=None, send_notifications=None, cancel=None, check_updates=None, **namedargs):
        if datastore is None:
            datastore = {}
        if send_response is not None:
            self.send_response = send_response
        if send_notifications is not None:
            self.send_notifications = send_notifications
        if cancel is not None:
            self.cancel = cancel
        if check_updates is not None:
            self.check_updates = check_updates
        datastore[subscribers_key] = []
        super(SubscriptionParticipantBehaviour, self).__init__(name, **namedargs)

        #
        # States
        #
        await_initiation_state = State(AwaitInitiationBehaviour(datastore=datastore, name="Await-initiation"))
        send_response_state = State(SendResponseBehaviour(datastore=datastore, send_response=self.send_response, name="Send-response"))
        check_updates_state = State(CheckUpdatesBehaviour(datastore=datastore, check_updates=self.check_updates, name="Check-updates"))
        send_notifications_state = State(SendNotificationBehaviour(datastore=datastore, send_notifications=self.send_notifications, name="Send-notifications"))
        process_cancel_state = State(ProcessCancelBehaviour(datastore=datastore, cancel=self.cancel, name="Process-cancel"))
        #
        self.first_state = await_initiation_state
        #
        # Transitions
        #
        self.add_transition(await_initiation_state, check_updates_state)
        self.add_transition(await_initiation_state, send_response_state, INITIATION_RECEIVED)
        self.add_transition(await_initiation_state, process_cancel_state, CANCEL_REQUESTED)
        self.add_transition(await_initiation_state, None, FINISHED)
        self.add_transition(send_response_state, await_initiation_state, RESPONSE_SENT)
        self.add_transition(process_cancel_state, await_initiation_state, CANCELLED)
        self.add_transition(check_updates_state, send_notifications_state, UPDATED)
        self.add_transition(check_updates_state, await_initiation_state, NOT_UPDATED)
        self.add_transition(send_notifications_state, await_initiation_state, NOTIFIED)

    def send_response(self):
        # Override this if necessary
        pass

    def send_notifications(self):
        # Override this if necessary
        pass

    def cancel(self):
        # Override this if necessary
        pass

    def check_updates(self):
        # Override this
        return False


##################################################################
# Subscription initiator (i.e., subscriber) behaviours
##################################################################


class InitiatorStateBehaviour(StateBehaviour):
    """Behaviour in a subscriber's finite state machine state.

       Includes check_cancel callback so that cancellation
       can be requested by initiator at any point in the 
       protocol sequence.
    """
    def __init__(self, name='', check_cancel=None, **namedargs):
        if check_cancel is not None:
            self.check_cancel = check_cancel
        super(InitiatorStateBehaviour, self).__init__(name, **namedargs)

    def action(self):
        self.sub_action()
        # "At any point in the IP, the initiator of the IP may cancel the interaction protocol"
        if self.check_cancel():
            self.result = CANCEL_SIGNALLED

    def check_cancel(self):
        # Override this if appropriate
        # Return true if subscription should be cancelled
        return False

    def sub_action(self):
        # Override this
        pass


class SendSubscriptionBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', content=None, **namedargs):
        self.content = content  # list of references to objects of interest
        super(SendSubscriptionBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        msg = ACLMessage(ACLMessage.SUBSCRIBE)
        msg.receivers.add(self.datastore[subscription_key])
        msg.content = self.content
        msg.set_conversation_id()
        self.agent.send_message(msg)
        self.result = INITIATION_SENT


class AwaitResponseBehaviour(InitiatorStateBehaviour):
    def sub_action(self):
        if message_key in self.datastore:
            # we are still busy with handling the previous message
            return
        msg = self.agent.get_message()
        if msg is None:
            self.result = default_key
        else:
            self.datastore[message_key] = msg
            self.result = RESPONSE_RECEIVED


class HandleResponseBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_response=None, **namedargs):
        if handle_response is not None:
            self.handle_response = handle_response
        super(HandleResponseBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        msg = self.datastore.get(message_key)
        self.handle_response()
        if msg is not None:
            perf = msg.performative
            item = msg.content
            # set result according to performative
            if perf == ACLMessage.AGREE:
                self.result = AGREE_RECEIVED
            elif perf == ACLMessage.INFORM:
                self.result = INFORM_RECEIVED
            elif perf == ACLMessage.REFUSE:
                self.result = REFUSE_RECEIVED
            else:
                self.result = FAILURE_RECEIVED
        else:
            self.result = RESPONSE_HANDLED

'''
Commented out
    ACCEPT_PROPOSAL = 0
    AGREE = 1
    CANCEL = 2
    CFP = 3
    CONFIRM = 4
    DISCONFIRM = 5
    FAILURE = 6
    INFORM = 7
    INFORM_IF = 8
    INFORM_REF = 9
    NOT_UNDERSTOOD = 10
    PROPAGATE = 21
    PROPOSE = 11
    PROXY = 20
    QUERY_IF = 12
    QUERY_REF = 13
    REFUSE = 14
    REJECT_PROPOSAL = 15
    REQUEST = 16
    REQUEST_WHEN = 17
    REQUEST_WHENEVER = 18
    SUBSCRIBE = 19
    UNKNOWN = -1
'''

class HandleAgreeBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_agree=None, **namedargs):
        if handle_agree is not None:
            self.handle_agree = handle_agree
        super(HandleAgreeBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        self.handle_agree()
        self.result = AGREE_HANDLED


class HandleRefuseBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_refuse=None, **namedargs):
        if handle_refuse is not None:
            self.handle_refuse = handle_refuse
        super(HandleRefuseBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        self.handle_refuse()
        self.result = REFUSE_HANDLED


class HandleInformBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_inform=None, **namedargs):
        if handle_inform is not None:
            self.handle_inform = handle_inform
        super(HandleInformBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        msg = self.datastore[message_key]
        content = msg.content
        self.handle_inform(content)
        self.result = INFORM_HANDLED


class HandleFailureBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_failure=None, **namedargs):
        if handle_failure is not None:
            self.handle_failure = handle_failure
        super(HandleFailureBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        self.handle_failure()
        self.result = FAILURE_HANDLED


class HandledResponseBehaviour(InitiatorStateBehaviour):
    def sub_action(self):
#        if message_key in self.datastore:  # not clear why this should not be the case
        del self.datastore[message_key]
        self.result = RESPONSE_HANDLED


class RequestCancelBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', cancel=None, **namedargs):
        if cancel is not None:
            self.cancel = cancel
        super(RequestCancelBehaviour, self).__init__(name, **namedargs)

    def action(self):  # Override action, not sub_action
        self.cancel()
        msg = ACLMessage(ACLMessage.CANCEL)
        msg.receivers.add(self.datastore[subscription_key])
        self.agent.send_message(msg)
        self.result = CANCEL_REQUESTED


class AwaitCancellationResultBehaviour(InitiatorStateBehaviour):
    def action(self):  # Override action, not sub_action
        msg = self.agent.get_message()
        self.result = default_key
        if msg is not None:
            perf = msg.performative
            if perf == ACLMessage.INFORM_DONE:
                # FIXME: Check whether or not cancel really succeeded
                del self.datastore[message_key]
                self.result = CANCEL_SUCCEEDED


class SubscriptionInitiatorBehaviour(FSMBehaviour):
    """Behaviour for subscriber role."""

    def __init__(self, name='', datastore=None, subscription=None, handle_response=None, handle_agree=None, handle_refuse=None, handle_inform=None, handle_failure=None, cancel=None, check_cancel=None, **namedargs):
        if datastore is None:
            datastore = {}
        if handle_response is not None:
            self.handle_response = handle_response
        if handle_agree is not None:
            self.handle_agree = handle_agree
        if handle_refuse is not None:
            self.handle_refuse = handle_refuse
        if handle_inform is not None:
            self.handle_inform = handle_inform
        if handle_failure is not None:
            self.handle_failure = handle_failure
        if cancel is not None:
            self.cancel = cancel
        if check_cancel is not None:
            self.check_cancel = check_cancel
        datastore[subscription_key] = subscription
        super(SubscriptionInitiatorBehaviour, self).__init__(name, **namedargs)
        #
        # States
        #
        send_initiation_state = State(SendSubscriptionBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Send-initiation"))
        await_response_state = State(AwaitResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Await-response"))
        handle_response_state = State(HandleResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_response=self.handle_response, name="Handle-response"))
        handled_response_state = State(HandledResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Handled-response"))
        handle_agree_state = State(HandleAgreeBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_agree=self.handle_agree, name="Handle-agree"))
        handle_refuse_state = State(HandleRefuseBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_refuse=self.handle_refuse, name="Handle-refuse"))
        handle_inform_state = State(HandleInformBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_inform=self.handle_inform, name="Handle-inform"))
        handle_failure_state = State(HandleFailureBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_failure=self.handle_failure, name="Handle-failure"))
        request_cancel_state = State(RequestCancelBehaviour(datastore=datastore, check_cancel=self.check_cancel, cancel=self.cancel, name="Request-cancel"))
        await_cancellation_result_state = State(AwaitCancellationResultBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Await-cancellation-result"))
        #
        self.first_state = send_initiation_state
        #
        # Transitions
        #
        states = [ send_initiation_state, await_response_state, handle_response_state, handled_response_state, handle_agree_state, handle_refuse_state, handle_inform_state, handle_failure_state, request_cancel_state, await_cancellation_result_state ]
        for state in states:
            self.add_transition(state, request_cancel_state, CANCEL_SIGNALLED)
        #
        self.add_transition(send_initiation_state, await_response_state, INITIATION_SENT)
        self.add_transition(await_response_state, await_response_state)
        self.add_transition(await_response_state, handle_response_state, RESPONSE_RECEIVED)
        self.add_transition(handle_response_state, handle_agree_state, AGREE_RECEIVED)
        self.add_transition(handle_response_state, handle_refuse_state, REFUSE_RECEIVED)
        self.add_transition(handle_response_state, handle_inform_state, INFORM_RECEIVED)
        self.add_transition(handle_response_state, handle_failure_state, FAILURE_RECEIVED)
        self.add_transition(handle_agree_state, handled_response_state, AGREE_HANDLED)
        self.add_transition(handle_refuse_state, handled_response_state, REFUSE_HANDLED)
        self.add_transition(handle_inform_state, handled_response_state, INFORM_HANDLED)
        self.add_transition(handle_failure_state, None, FAILURE_HANDLED)
        self.add_transition(handled_response_state, await_response_state, RESPONSE_HANDLED)
        self.add_transition(handle_response_state, await_response_state, RESPONSE_HANDLED)
        self.add_transition(request_cancel_state, await_cancellation_result_state, CANCEL_REQUESTED)
        self.add_transition(await_cancellation_result_state, await_cancellation_result_state)
        self.add_transition(await_cancellation_result_state, None, CANCEL_SUCCEEDED)
        self.add_transition(await_cancellation_result_state, None, CANCEL_FAILED) # FIXME: Retry cancellation?
        self.add_transition(await_response_state, None, FINISHED)

    def handle_response(self):
        # Override this if necessary
        pass

    def handle_agree(self):
        # Override this if necessary
        pass

    def handle_refuse(self):
        # Override this if necessary
        pass

    def handle_inform(self):
        # Override this if necessary
        pass

    def handle_failure(self):
        # Override this if necessary
        pass

    def cancel(self):
        # Override this if necessary
        pass

    def check_cancel(self):
        # Override this if necessary
        return False
