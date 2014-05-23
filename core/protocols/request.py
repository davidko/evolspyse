"""Spyse FIPA request protocol module"""

# FIPA Request Interaction Protocol
# http://www.fipa.org/specs/fipa00026/SC00026H.html
#

import time
from datetime import datetime
from random import randint
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour, State
from spyse.core.content.content import ACLMessage

# Keys for datastore
message_key = "message_key"
conversation_key = "conversation_key"
store_key = "store_key"
customer_key = "customer_key"
request_key = "request_key"
default_key = "default_key"
timeout_key = "timeout_key"
event_time_key = "event_time_key"

# FSM event names
PARTICIPANT_NOT_FOUND = "PARTICIPANT_NOT_FOUND"
INITIATION_SENT = "INITIATION_SENT"
RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
AGREE_RECEIVED = "AGREE_RECEIVED"
REFUSE_RECEIVED = "REFUSE_RECEIVED"
INFORM_RECEIVED = "INFORM_RECEIVED"
INFORM_DONE_RECEIVED = "INFORM_DONE_RECEIVED"
FAILURE_RECEIVED = "FAILURE_RECEIVED"
AGREE_HANDLED = "AGREE_HANDLED"
REFUSE_HANDLED = "REFUSE_HANDLED"
INFORM_HANDLED = "INFORM_HANDLED"
INFORM_DONE_HANDLED = "INFORM_DONE_HANDLED"
FAILURE_HANDLED = "FAILURE_HANDLED"
RESPONSE_HANDLED = "RESPONSE_HANDLED"
CANCEL_SIGNALLED = "CANCEL_SIGNALLED"
CANCEL_REQUESTED = "CANCEL_REQUESTED"
CANCEL_SUCCEEDED = "CANCEL_SUCCEEDED"
CANCEL_FAILED = "CANCEL_FAILED"
CANCELLED = "CANCELLED"
FINISHED = "FINISHED"
TIMEOUT = "TIMEOUT"
#
INITIATION_RECEIVED = "INITIATION_RECEIVED"
REQUEST_PERFORMED = "REQUEST_PERFORMED"
RESPONSE_SENT = "RESPONSE_SENT"
RESULT_SENT = "RESULT_SENT"
UPDATED = "UPDATED"
NOT_UPDATED = "NOT_UPDATED"
NOTIFIED = "NOTIFIED"


class StateBehaviour(Behaviour):
    """Behaviour in a request finite state machine state.

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
# Request participant behaviours
##################################################################


class AwaitInitiationBehaviour(StateBehaviour):
    def action(self):
        if message_key in self.datastore:
            self.result = default_key
        elif conversation_key in self.datastore:
            msg = self.agent.get_message({'conversation-id': self.datastore[conversation_key]})            
        else:
            msg = self.agent.get_message({'performative': ACLMessage.REQUEST})
        
        if msg is None:
            self.result = default_key
        elif msg.performative == ACLMessage.CANCEL:
            self.datastore[message_key] = msg
            self.result = CANCEL_REQUESTED
        elif msg.performative == ACLMessage.REQUEST:
            self.datastore[message_key] = msg
            self.datastore[customer_key] = msg.sender
            self.datastore[conversation_key] = msg.conversation_id
            self.result = INITIATION_RECEIVED
        else:
            print 'REQUEST PROTOCOL ERROR',self.datastore
            self.result = default_key


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
            reply.sender = self.agent.aid
            self.agent.send_message(reply)
            self.result = RESPONSE_SENT
        else:
            self.result = default_key
            
class PerformRequestBehaviour(StateBehaviour):
    def __init__(self, name='', perform_request=None, **namedargs):
        if perform_request is not None:
            self.perform_request = perform_request
        super(PerformRequestBehaviour, self).__init__(name, **namedargs)
        
    def action(self):
        content = self.datastore[message_key].content
        if self.perform_request(content):
            self.result = REQUEST_PERFORMED
        else:
            self.result = default_key
 

class SendResultBehaviour(StateBehaviour):
    def __init__(self, name='', send_result=None, **namedargs):
        if send_result is not None:
            self.send_result = send_result
        super(SendResultBehaviour, self).__init__(name, **namedargs)

    def action(self):
        content = self.datastore[message_key].content
        result = self.send_result()
        msg = self.datastore[message_key]
        if result is None:
            reply = msg.create_reply(ACLMessage.INFORM_DONE)
        else:
            reply = msg.create_reply(ACLMessage.INFORM)
            reply.content = result

        self.agent.send_message(reply)
        del self.datastore[message_key]
        del self.datastore[conversation_key]
        self.result = RESULT_SENT


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
            self.datastore[customer_key] = None
            self.result = CANCELLED
        else:
            self.result = default_key


class RequestParticipantBehaviour(FSMBehaviour):
    """Behaviour for particpant role"""

    def __init__(self, name='', datastore=None, send_response=None, perform_request=None, send_result=None, cancel=None, **namedargs):
        if datastore is None:
            datastore = {}
        if send_response is not None:
            self.send_response = send_response
        if perform_request is not None:
            self.perform_request = perform_request
        if send_result is not None:
            self.send_result = send_result
        if cancel is not None:
            self.cancel = cancel

        datastore[customer_key] = None
        super(RequestParticipantBehaviour, self).__init__(name, **namedargs)

        #
        # States
        #
        await_initiation_state = State(AwaitInitiationBehaviour(datastore=datastore, name="Await-initiation"))
        send_response_state = State(SendResponseBehaviour(datastore=datastore, send_response=self.send_response, name="Send-response"))
        perform_request_state = State(PerformRequestBehaviour(datastore=datastore, perform_request=self.perform_request, name="Perform-Request"))
        send_result_state = State(SendResultBehaviour(datastore=datastore, send_result=self.send_result, name="Send-result"))
        process_cancel_state = State(ProcessCancelBehaviour(datastore=datastore, cancel=self.cancel, name="Process-cancel"))
        #
        self.first_state = await_initiation_state
        #
        # Transitions
        #
        self.add_transition(await_initiation_state, await_initiation_state)
        self.add_transition(await_initiation_state, send_response_state, INITIATION_RECEIVED)
        self.add_transition(await_initiation_state, process_cancel_state, CANCEL_REQUESTED)
        self.add_transition(await_initiation_state, None, FINISHED)
        self.add_transition(send_response_state, perform_request_state, RESPONSE_SENT)
        self.add_transition(perform_request_state,perform_request_state)
        self.add_transition(perform_request_state,send_result_state,REQUEST_PERFORMED)
        self.add_transition(send_result_state, await_initiation_state, RESULT_SENT)
        self.add_transition(process_cancel_state, None, CANCELLED)
        

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
# Subscription initiator behaviours
##################################################################


class InitiatorStateBehaviour(StateBehaviour):
    """Behaviour in a request's finite state machine state.

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


class SendRequestBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', content=None, handle_no_participant=None, **namedargs):
        self.content = content  # list of references to objects of interest
        self.handle_no_participant = handle_no_participant
        super(SendRequestBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        msg = ACLMessage(ACLMessage.REQUEST)
        msg.receivers.add(self.datastore[store_key])
        msg.content = self.datastore[request_key]
        msg.set_conversation_id()
        self.datastore[conversation_key] = msg.conversation_id
        if self.agent.send_message(msg):
            self.result = INITIATION_SENT
            self.datastore[event_time_key] = time.time()
        else:
            if self.handle_no_participant is not None:
                self.handle_no_participant(self.datastore[store_key])
            self.result = PARTICIPANT_NOT_FOUND


class AwaitResponseBehaviour(InitiatorStateBehaviour):
    def sub_action(self):
        if message_key in self.datastore:
            # we are still busy with handling the previous message
            return
        msg = self.agent.get_message({'conversation-id': self.datastore[conversation_key]})
        #msg = self.agent.get_message()
        
        if msg is None:
            timeout = self.datastore[timeout_key]
            if timeout is not None and \
                    (time.time() - self.datastore[event_time_key]) > timeout:
                self.result = TIMEOUT
            else:
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
            elif perf == ACLMessage.INFORM_DONE:
                self.result = INFORM_DONE_RECEIVED
            elif perf == ACLMessage.REFUSE:
                self.result = REFUSE_RECEIVED
            else:
                self.result = FAILURE_RECEIVED
        else:
            self.result = RESPONSE_HANDLED

class HandleAgreeBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_agree=None, **namedargs):
        if handle_agree is not None:
            self.handle_agree = handle_agree
        super(HandleAgreeBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        self.handle_agree()
        del self.datastore[message_key]
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
        
class HandleInformDoneBehaviour(InitiatorStateBehaviour):
    def __init__(self, name='', handle_inform_done=None, **namedargs):
        if handle_inform_done is not None:
            self.handle_inform_done = handle_inform_done
        super(HandleInformDoneBehaviour, self).__init__(name, **namedargs)

    def sub_action(self):
        msg = self.datastore[message_key]
        content = msg.content
        self.handle_inform_done(content)
        self.result = INFORM_DONE_HANDLED


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
        msg.conversation_id = self.datastore[conversation_key]
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


class RequestInitiatorBehaviour(FSMBehaviour):
    """Behaviour for initiator role."""

    def __init__(self, name='', datastore=None, store=None, request=None,
            handle_no_participant=None, handle_response=None, handle_agree=None,
            handle_refuse=None, handle_inform=None, handle_inform_done=None,
            handle_failure=None, cancel=None, check_cancel=None, timeout=None, 
            **namedargs):
        if datastore is None:
            datastore = {}
        if handle_no_participant is not None:
            self.handle_no_participant = handle_no_participant
        if handle_response is not None:
            self.handle_response = handle_response
        if handle_agree is not None:
            self.handle_agree = handle_agree
        if handle_refuse is not None:
            self.handle_refuse = handle_refuse
        if handle_inform is not None:
            self.handle_inform = handle_inform
        if handle_inform_done is not None:    
            self.handle_inform_done = handle_inform_done
        if handle_failure is not None:
            self.handle_failure = handle_failure
        if cancel is not None:
            self.cancel = cancel
        if check_cancel is not None:
            self.check_cancel = check_cancel
        datastore[timeout_key] = timeout
        datastore[store_key] = store
        datastore[request_key] = request
        super(RequestInitiatorBehaviour, self).__init__(name, **namedargs)
        #
        # States
        #
        send_initiation_state = State(SendRequestBehaviour(datastore=datastore, handle_no_participant=self.handle_no_participant, check_cancel=self.check_cancel, name="Send-initiation"))
        await_response_state = State(AwaitResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Await-response"))
        handle_response_state = State(HandleResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_response=self.handle_response, name="Handle-response"))
        handled_response_state = State(HandledResponseBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Handled-response"))
        handle_agree_state = State(HandleAgreeBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_agree=self.handle_agree, name="Handle-agree"))
        handle_refuse_state = State(HandleRefuseBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_refuse=self.handle_refuse, name="Handle-refuse"))
        handle_inform_state = State(HandleInformBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_inform=self.handle_inform, name="Handle-inform"))
        handle_inform_done_state = State(HandleInformDoneBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_inform_done=self.handle_inform_done, name="Handle-inform-done"))
        handle_failure_state = State(HandleFailureBehaviour(datastore=datastore, check_cancel=self.check_cancel, handle_failure=self.handle_failure, name="Handle-failure"))
        request_cancel_state = State(RequestCancelBehaviour(datastore=datastore, check_cancel=self.check_cancel, cancel=self.cancel, name="Request-cancel"))
        await_cancellation_result_state = State(AwaitCancellationResultBehaviour(datastore=datastore, check_cancel=self.check_cancel, name="Await-cancellation-result"))
        #
        self.first_state = send_initiation_state
        #
        # Transitions
        #
        states = [ send_initiation_state, await_response_state, handle_response_state, handled_response_state, handle_agree_state, handle_refuse_state, handle_inform_state, handle_inform_done_state, handle_failure_state, request_cancel_state, await_cancellation_result_state ]
        for state in states:
            self.add_transition(state, request_cancel_state, CANCEL_SIGNALLED)
        #
        self.add_transition(send_initiation_state, await_response_state, INITIATION_SENT)
        self.add_transition(send_initiation_state, None, PARTICIPANT_NOT_FOUND)
        self.add_transition(await_response_state, await_response_state)
        self.add_transition(await_response_state, handle_response_state, RESPONSE_RECEIVED)
        self.add_transition(handle_response_state, handle_agree_state, AGREE_RECEIVED)
        self.add_transition(handle_response_state, handle_refuse_state, REFUSE_RECEIVED)
        self.add_transition(handle_response_state, handle_inform_state, INFORM_RECEIVED)
        self.add_transition(handle_response_state, handle_inform_done_state, INFORM_DONE_RECEIVED)
        self.add_transition(handle_response_state, handle_failure_state, FAILURE_RECEIVED)
        self.add_transition(handle_agree_state, await_response_state, AGREE_HANDLED)
        self.add_transition(handle_refuse_state, handled_response_state, REFUSE_HANDLED)
        self.add_transition(handle_inform_state, handled_response_state, INFORM_HANDLED)
        self.add_transition(handle_inform_done_state, handled_response_state, INFORM_DONE_HANDLED)
        self.add_transition(handle_failure_state, None, FAILURE_HANDLED)
        self.add_transition(handled_response_state, None, RESPONSE_HANDLED)
        #self.add_transition(handle_response_state, await_response_state, RESPONSE_HANDLED)
        self.add_transition(request_cancel_state, await_cancellation_result_state, CANCEL_REQUESTED)
        self.add_transition(await_cancellation_result_state, await_cancellation_result_state)
        self.add_transition(await_cancellation_result_state, None, CANCEL_SUCCEEDED)
        self.add_transition(await_cancellation_result_state, None, CANCEL_FAILED) # FIXME: Retry cancellation?
        self.add_transition(await_response_state, None, FINISHED)

    def handle_no_participant(self, aid):
        # Override this if necesarry
        pass

    def handle_response(self):
        # Override this if necessary
        pass

    def handle_agree(self):
        # Override this if necessary
        pass

    def handle_refuse(self):
        # Override this if necessary
        pass

    def handle_inform(self, inform_result):
        # Override this if necessary
        pass
    
    def handle_inform_done(self, inform_result):
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
