"""Spyse FIPA ContractNet protocol module"""

#
# FIPA Contract Net Interaction Protocol
# http://www.fipa.org/specs/fipa00029/SC00029H.html
#

import time
from datetime import datetime
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour, State
from spyse.core.content.content import ACLMessage, MessageTemplate, TemplateSet
from spyse.core.protocols.protocols import Protocol

verbose = False


class StateBehaviour(Behaviour):
    """Behaviour in a Contract Net finite state machine state.

       Includes reference to a common data store needed by particular
       the behaviours in all the states of a FSM.
    """
    def __init__(self, name='', datastore=None, **namedargs):
        self.datastore = datastore
        Behaviour.__init__(self, name, **namedargs)


##################################################################
# Contract Net initiator
##################################################################

class ContractNetInitiatorBehaviour(FSMBehaviour):

    default_key = "default"
    providers_key = "providers"
    responses_key = "responses"

    CANCELLING = "Cancelling"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    FAILURE = "Failure"

    INITIATION_SENT = "Initiation-Sent"
    RESPONSE_RECEIVED = "Response-Received"
    PROPOSE_RECEIVED = "Propose-Received"
    REFUSE_RECEIVED = "Refuse-Received"
    FAILURE_RECEIVED = "Failure-Received"
    INFORM_DONE_RECEIVED = "Inform-Done-Received"
    INFORM_RESULT_RECEIVED = "Inform-Result-Received"
    PROPOSE_HANDLED = "Propose-Handled"
    REFUSE_HANDLED = "Refuse-Handled"
    RESPONSE_HANDLED = "Response-Handled"
    ALL_RESPONSES_RECEIVED = "All-Responses-Received"
    DEADLINE_REACHED = "Deadline-Reached"
    PROPOSAL_SELECTED = "Proposal-Selected"
    CONCLUSION_SENT = "Conclusion-Sent"
    RESULT_RECEIVED = "Result-Received"

    class SendCallBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            msg = ACLMessage(ACLMessage.CFP)
            msg.protocol = Protocol.FIPA_CONTRACT_NET
    #        try:
            providers = self.datastore[ContractNetInitiatorBehaviour.providers_key]
            for p in providers:
                msg.receivers.add(p)
            msg.content = self.datastore['call']
            msg.set_conversation_id()
            self.agent.send_message(msg)
            self.result = ContractNetInitiatorBehaviour.INITIATION_SENT
    #        except:
    #            pass
    #            #self.result = ContractNetInitiatorBehaviour.INITIATION_NOT_SENT ???
    
    
    class ReceiveResponseBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, deadline=None, **namedargs):
            self.__deadline = deadline
            StateBehaviour.__init__(self, name, datastore, **namedargs)
            self.datastore['proposals'] = []
            self.datastore[ContractNetInitiatorBehaviour.responses_key] = []
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            template = MessageTemplate(performative=TemplateSet([ACLMessage.PROPOSE, ACLMessage.REFUSE]))
            template.protocol = Protocol.FIPA_CONTRACT_NET
            msg = self.agent.get_message(template)
            if time.time() >= self.__deadline:
                self.result = ContractNetInitiatorBehaviour.DEADLINE_REACHED
            elif msg is None:
                self.result = ContractNetInitiatorBehaviour.default_key
            else:
                self.datastore[ContractNetInitiatorBehaviour.responses_key].append(msg.sender)
                self.datastore['response'] = msg
                self.result = ContractNetInitiatorBehaviour.RESPONSE_RECEIVED
    
    
    class HandleResponseBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            response = self.datastore['response']
            if response.performative==ACLMessage.PROPOSE:
                self.result = ContractNetInitiatorBehaviour.PROPOSE_RECEIVED
            elif response.performative==ACLMessage.REFUSE:
                self.result = ContractNetInitiatorBehaviour.REFUSE_RECEIVED
            else:
                self.result = ContractNetInitiatorBehaviour.FAILURE    # TODO: add in FSM
    
    
    class HandleProposeBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            proposal = self.datastore['response']
            self.datastore['proposals'].append(proposal)
            self.result = ContractNetInitiatorBehaviour.PROPOSE_HANDLED
    
    
    class HandleRefuseBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetInitiatorBehaviour.REFUSE_HANDLED
    
    
    class HandledResponseBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            responses = self.datastore[ContractNetInitiatorBehaviour.responses_key]
            providers = self.datastore[ContractNetInitiatorBehaviour.providers_key]
            if len(responses)==len(providers):
                self.result = ContractNetInitiatorBehaviour.ALL_RESPONSES_RECEIVED
            else:
                self.result = ContractNetInitiatorBehaviour.RESPONSE_HANDLED
    
    
    class SelectProposalBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, select_proposal=None, **namedargs):
            if select_proposal is not None:
                self.select_proposal = select_proposal
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            proposals = self.datastore['proposals']
            contract = self.select_proposal(proposals)
            self.datastore['contract'] = contract
            self.result = ContractNetInitiatorBehaviour.PROPOSAL_SELECTED
    
    
    class SendConclusionBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            proposals = self.datastore['proposals']
            contract = self.datastore['contract']
            for p in proposals:
                conclusion = p.create_reply()
                if p == contract:
                    conclusion.performative = ACLMessage.ACCEPT_PROPOSAL
                    conclusion.content = p.content
                else:
                    conclusion.performative = ACLMessage.REJECT_PROPOSAL
                self.agent.send_message(conclusion)
            self.result = ContractNetInitiatorBehaviour.CONCLUSION_SENT
    
    
    class ReceiveResultBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            template = MessageTemplate(performative=TemplateSet([ACLMessage.INFORM_IF, ACLMessage.INFORM_REF, ACLMessage.FAILURE]))
            template.protocol = Protocol.FIPA_CONTRACT_NET
            msg = self.agent.get_message(template)
            if msg is None:
                self.result = ContractNetInitiatorBehaviour.default_key
            else:
                self.datastore['result'] = msg
                self.result = ContractNetInitiatorBehaviour.RESULT_RECEIVED
    
    class HandleResultBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            result = self.datastore['result']
            if result.performative == ACLMessage.INFORM_IF:  # INFORM_DONE    ???
                self.result = ContractNetInitiatorBehaviour.INFORM_DONE_RECEIVED
            elif result.performative == ACLMessage.INFORM_REF:  # INFORM_RESULT    ???
                self.result = ContractNetInitiatorBehaviour.INFORM_RESULT_RECEIVED
            else:
                self.result = ContractNetInitiatorBehaviour.FAILURE_RECEIVED
    
    
    class HandleInformDoneBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, process_result=None, **namedargs):
            if process_result is not None:
                self.process_result = process_result
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.process_result()
            self.result = ContractNetInitiatorBehaviour.FINISHED
    
    
    class HandleInformResultBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, process_result=None, **namedargs):
            if process_result is not None:
                self.process_result = process_result
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.process_result(self.datastore['result'])
            self.result = ContractNetInitiatorBehaviour.FINISHED
    
    
    class HandleFailureBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetInitiatorBehaviour.FINISHED
    
    
    class InitiatorCancelBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetInitiatorBehaviour.CANCELLED
    
    
    class InitiatorFinishBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetInitiatorBehaviour.FINISHED


    def __init__(self, name='', datastore=None, deadline=None, select_proposal=None, process_result=None, **namedargs):
        if datastore is None:
            datastore = {}
        if deadline is None:
            deadline = time.time() + 60
        if select_proposal is not None:
            self.select_proposal = select_proposal
        if process_result is not None:
            self.process_result = process_result
        super(ContractNetInitiatorBehaviour, self).__init__(name, **namedargs)
        #
        # States
        #
        send_initiation_state = State(self.SendCallBehaviour(datastore=datastore, name="Send-Initiation"))
        receive_response_state = State(self.ReceiveResponseBehaviour(datastore=datastore, deadline=deadline, name="Receive-Response"))
        handle_response_state = State(self.HandleResponseBehaviour(datastore=datastore, name="Handle-Response"))
        handle_propose_state = State(self.HandleProposeBehaviour(datastore=datastore, name="Handle-Propose"))
        handle_refuse_state = State(self.HandleRefuseBehaviour(datastore=datastore, name="Handle-Refuse"))
        handled_response_state = State(self.HandledResponseBehaviour(datastore=datastore, name="Handled-Response"))
        select_proposal_state = State(self.SelectProposalBehaviour(datastore=datastore, select_proposal=self.select_proposal, name="Select-Proposal"))
        send_conclusion_state = State(self.SendConclusionBehaviour(datastore=datastore, name="Send-Conclusion"))
        receive_result_state = State(self.ReceiveResultBehaviour(datastore=datastore, name="Receive-Result"))
        handle_result_state = State(self.HandleResultBehaviour(datastore=datastore, name="Handle-Result"))
        handle_inform_done_state = State(self.HandleInformDoneBehaviour(datastore=datastore, process_result=self.process_result, name="Handle-Inform-Done"))
        handle_inform_result_state = State(self.HandleInformResultBehaviour(datastore=datastore, process_result=self.process_result, name="Handle-Inform-Result"))
        handle_failure_state = State(self.HandleFailureBehaviour(datastore=datastore, name="Handle-Failure"))
        cancel_state = State(self.InitiatorCancelBehaviour(datastore=datastore, name="Cancel"))
        #
        self.first_state = send_initiation_state
        #
        # Transitions
        #
        self.add_transition(send_initiation_state, receive_response_state, self.INITIATION_SENT)
        self.add_transition(receive_response_state, receive_response_state)
        self.add_transition(receive_response_state, handle_response_state, self.RESPONSE_RECEIVED)
        self.add_transition(handle_response_state, handle_propose_state, self.PROPOSE_RECEIVED)
        self.add_transition(handle_response_state, handle_refuse_state, self.REFUSE_RECEIVED)
        self.add_transition(handle_propose_state, handled_response_state, self.PROPOSE_HANDLED)
        self.add_transition(handle_refuse_state, handled_response_state, self.REFUSE_HANDLED)
        self.add_transition(handled_response_state, receive_response_state, self.RESPONSE_HANDLED)
        self.add_transition(handled_response_state, select_proposal_state, self.ALL_RESPONSES_RECEIVED)
        #self.add_transition(handled_response_state, select_proposal_state, self.DEADLINE_REACHED)
        self.add_transition(receive_response_state, select_proposal_state, self.DEADLINE_REACHED)
        self.add_transition(select_proposal_state, send_conclusion_state, self.PROPOSAL_SELECTED)
        self.add_transition(send_conclusion_state, receive_result_state, self.CONCLUSION_SENT)
        self.add_transition(receive_result_state, receive_result_state)
        self.add_transition(receive_result_state, handle_result_state, self.RESULT_RECEIVED)
        self.add_transition(handle_result_state, handle_inform_done_state, self.INFORM_DONE_RECEIVED)
        self.add_transition(handle_result_state, handle_inform_result_state, self.INFORM_RESULT_RECEIVED)
        self.add_transition(handle_result_state, handle_failure_state, self.FAILURE_RECEIVED)
        self.add_transition(handle_inform_done_state, None, self.FINISHED)
        self.add_transition(handle_inform_result_state, None, self.FINISHED)
        self.add_transition(handle_failure_state, None, self.FINISHED)
        #
        self.add_transition(receive_response_state, cancel_state, self.CANCELLING)
        self.add_transition(receive_result_state, cancel_state, self.CANCELLING)
        self.add_transition(cancel_state, None, self.CANCELLED)
        self.add_transition(receive_response_state, None, self.FINISHED)

    def select_proposal(self, proposals):
        # Override this if necessary
        for proposal in proposals:
            return proposal  # Return the first proposal

    def process_result(self, result=None):
        # Override this if necessary
        pass


####################################################
# Contract Net participant
####################################################
class ContractNetParticipantBehaviour(FSMBehaviour):

    default_key = "default"

    CANCELLING = "Cancelling"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    FAILURE = "Failure"

    INITIATION_RECEIVED = "Initiation-Received"
    PROPOSAL_MADE = "Proposal-Made"
    RESPONSE_SENT = "Response-Sent"
    CONCLUSION_RECEIVED = "Conclusion-Received"
    ACCEPT_RECEIVED = "Accept-Received"
    REJECT_RECEIVED = "Reject-Received"
    ACCEPT_HANDLED = "Accept-Handled"
    REJECT_HANDLED = "Reject-Handled"
    CONCLUSION_HANDLED = "Conclusion-Handled"
    
    class ReceiveCallBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, **namedargs):
            StateBehaviour.__init__(self, name, datastore, **namedargs)
            self.datastore['calls'] = []
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.datastore['id'] = self.agent.name
    
            template = MessageTemplate(performative=TemplateSet([ACLMessage.CFP]))
            template.protocol = Protocol.FIPA_CONTRACT_NET
            msg = self.agent.get_message(template)
            if msg is None:
                self.result = ContractNetParticipantBehaviour.default_key
            else:
                self.datastore['call'] = msg
                self.datastore['calls'].append(msg)
                self.result = ContractNetParticipantBehaviour.INITIATION_RECEIVED
    
    
    class MakeProposalBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, make_proposal=None, **namedargs):
            if make_proposal is not None:
                self.make_proposal = make_proposal
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            proposal = self.make_proposal(self.datastore['call'])
            if proposal is None:
                self.result = ContractNetParticipantBehaviour.default_key
            else:
                self.datastore['proposal'] = proposal
                self.result = ContractNetParticipantBehaviour.PROPOSAL_MADE
    
    
    class SendResponseBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, **namedargs):
            StateBehaviour.__init__(self, name, datastore, **namedargs)
            self.datastore['proposals'] = []
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            proposal = self.datastore['proposal']
            self.datastore['proposals'].append(proposal)
            self.agent.send_message(proposal)
            self.result = ContractNetParticipantBehaviour.RESPONSE_SENT
    
    
    class ReceiveConclusionBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            template = MessageTemplate(performative=TemplateSet([ACLMessage.ACCEPT_PROPOSAL, ACLMessage.REJECT_PROPOSAL]))
            template.protocol = Protocol.FIPA_CONTRACT_NET
            msg = self.agent.get_message(template)
            if msg is None:
                self.result = ContractNetParticipantBehaviour.default_key
            else:
                self.datastore['conclusion'] = msg
                self.result = ContractNetParticipantBehaviour.CONCLUSION_RECEIVED
    
    
    class HandleConclusionBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            conclusion = self.datastore['conclusion']
            if conclusion.performative == ACLMessage.ACCEPT_PROPOSAL:
                self.result = ContractNetParticipantBehaviour.ACCEPT_RECEIVED
            elif conclusion.performative == ACLMessage.REJECT_PROPOSAL:
                self.result = ContractNetParticipantBehaviour.REJECT_RECEIVED
            else:
                self.result = ContractNetParticipantBehaviour.FAILURE  # TODO: add in FSM
    
    
    class HandleAcceptBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, execute_contract=None, **namedargs):
            if execute_contract is not None:
                self.execute_contract = execute_contract
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            conclusion = self.datastore['conclusion']
            result = self.execute_contract(conclusion)
            if result is None:
                self.result = ContractNetParticipantBehaviour.default_key
            else:
                reply = conclusion.create_reply()
                if result is False:
                    reply.performative = ACLMessage.FAILURE
                elif result is True:
                    reply.performative = ACLMessage.INFORM_IF  # INFORM_DONE
                else:
                    reply.performative = ACLMessage.INFORM_REF  # INFORM_RESULT
                    reply.content = result
                self.agent.send_message(reply)
                self.result = ContractNetParticipantBehaviour.ACCEPT_HANDLED
    
    
    class HandleRejectBehaviour(StateBehaviour):
        def __init__(self, name='', datastore=None, forget_contract=None, **namedargs):
            if forget_contract is not None:
                self.forget_contract = forget_contract
            StateBehaviour.__init__(self, name, datastore, **namedargs)
    
        def action(self):
            if verbose is True: print self.agent.name, self.name
            conclusion = self.datastore['conclusion']
            self.forget_contract(conclusion)
            self.result = ContractNetParticipantBehaviour.REJECT_HANDLED
    
    
    class HandledConclusionBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetParticipantBehaviour.CONCLUSION_HANDLED
    
    
    class ParticipantCancelBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetParticipantBehaviour.CANCELLED
    
    
    class ParticipantFinishBehaviour(StateBehaviour):
        def action(self):
            if verbose is True: print self.agent.name, self.name
            self.result = ContractNetParticipantBehaviour.FINISHED


    def __init__(self, name='', datastore=None, deadline=None, make_proposal=None, execute_contract=None, forget_contract=None, **namedargs):
        if datastore is None:
            datastore = {}
        if deadline is None:
            deadline = time.time() + 60
        if make_proposal is not None:
            self.make_proposal = make_proposal
        if execute_contract is not None:
            self.execute_contract = execute_contract
        if forget_contract is not None:
            self.forget_contract = forget_contract
        super(ContractNetParticipantBehaviour, self).__init__(name, **namedargs)
        #
        # States
        #
        receive_initiation_state = State(self.ReceiveCallBehaviour(datastore=datastore, name="Receive-Initiation"))
        make_proposal_state = State(self.MakeProposalBehaviour(datastore=datastore, make_proposal=self.make_proposal, name="Make-Proposal"))
        send_response_state = State(self.SendResponseBehaviour(datastore=datastore, name="Send-Response"))
        receive_conclusion_state = State(self.ReceiveConclusionBehaviour(datastore=datastore, name="Receive-Conclusion"))
        handle_conclusion_state = State(self.HandleConclusionBehaviour(datastore=datastore, name="Handle-Conclusion"))
        handle_accept_proposal_state = State(self.HandleAcceptBehaviour(datastore=datastore, execute_contract=self.execute_contract, name="Handle-Accept-Proposal"))
        handle_reject_proposal_state = State(self.HandleRejectBehaviour(datastore=datastore, forget_contract=self.forget_contract, name="Handle-Reject-Proposal"))
        handled_conclusion_state = State(self.HandledConclusionBehaviour(datastore=datastore, name="Handled-Conclusion"))
        cancel_state = State(self.ParticipantCancelBehaviour(datastore=datastore, name="Cancel"))
        #
        self.first_state = receive_initiation_state
        #
        # Transitions
        #
        self.add_transition(receive_initiation_state, receive_initiation_state)
        self.add_transition(receive_initiation_state, make_proposal_state, self.INITIATION_RECEIVED)
        self.add_transition(make_proposal_state, make_proposal_state)
        self.add_transition(make_proposal_state, send_response_state, self.PROPOSAL_MADE)
        self.add_transition(send_response_state, receive_conclusion_state, self.RESPONSE_SENT)
        self.add_transition(receive_conclusion_state, receive_conclusion_state)
        self.add_transition(receive_conclusion_state, handle_conclusion_state, self.CONCLUSION_RECEIVED)
        self.add_transition(handle_conclusion_state, handle_accept_proposal_state, self.ACCEPT_RECEIVED)
        self.add_transition(handle_conclusion_state, handle_reject_proposal_state, self.REJECT_RECEIVED)
        self.add_transition(handle_accept_proposal_state, handled_conclusion_state, self.ACCEPT_HANDLED)
        self.add_transition(handle_reject_proposal_state, handled_conclusion_state, self.REJECT_HANDLED)
        self.add_transition(handled_conclusion_state, receive_initiation_state, self.CONCLUSION_HANDLED)
        self.add_transition(receive_initiation_state, cancel_state, self.CANCELLING)
        self.add_transition(cancel_state, None, self.CANCELLED)
        self.add_transition(receive_initiation_state, None, self.FINISHED)

    def make_proposal(self, call):
        # Override this
        # Return a proposal
        raise Exception

    def execute_contract(self, conclusion):
        # Override this if necessary
        return None

    def forget_contract(self, conclusion):
        # Override this if necessary
        pass

