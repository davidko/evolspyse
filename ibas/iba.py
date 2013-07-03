from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour, TickerBehaviour
from spyse.core.protocols.request import RequestParticipantBehaviour
from spyse.core.protocols import request
from spyse.core.content.content import ACLMessage
from spyse.core.agents.aid import AID

from node import Node, Attribute, Statement
from ibas_global import IBASGlobal

import Pyro.core
import time
import copy
import urllib2
import thread
import threading
from xml.dom import minidom
from random import randint
from datetime import datetime, timedelta

ONE_HOUR = timedelta(hours=1)
ONE_MINUTE = timedelta(minutes=1)
ONE_SECOND = timedelta(seconds=1)
TWO_SECONDS = timedelta(seconds=2)

class SuspendBehaviour(Behaviour):
    """ Suspend the agent whenever possible """
    def setup(self):
        pass
    
    def action(self):
        if self.agent.allow_sleep:
            self.agent.go_sleep(in_mem=False)
            pass                
                
class MoveBehaviour(Behaviour):
    """ Move the IBA to another container that's less crowded then it's current """
    def action(self):
        if datetime.now() >= self.agent.move_time:
            target = self.agent.mts.ams.get_move_target()
            if target is not None:
                IBASGlobal.print_message(self.agent.shortname+' moving to '+str(target),1)
                self.agent.remove_behaviour(self.agent.rpb)
                self.agent.rpb = None
                self.agent.move(target)
            else:
                # if an agent is not going to move it can go to sleep
                self.agent.allow_sleep=True
                
class AvailabilityBehaviour(Behaviour):
    """ Check to see if a website is still accessible, send result to the logger agent """
    def setup(self):
        self.result = None
    
    def action(self):
        if datetime.now() >= self.agent.check_time:
            if self.result is None:
                self.result = ""
                threading.Thread(target = self.__check, args=()).start()
            elif self.result != "":
                msg = ACLMessage(ACLMessage.INFORM)
                msg.receivers.add(AID('Logger Agent'))
                msg.content = self.result
                self.agent.send_message(msg)
                self.agent.check_time = datetime.now() + ONE_HOUR
                self.result = None
    
    def __check(self):
        target="http://void"
        try:
            for att in self.agent.node.attributes:
                if str(att.type) == '7d66a5-ea25eaa5bc-bffe39a6a8970943449682fd6b671537':
                    target = str(att.value)
                    break
            urllib2.urlopen(target)
            self.result = 'AVAILABILITY CHECK SUCCEEDED-'+target
        except:
            self.result = 'AVAILABILITY CHECK FAILED-'+target

class IBA(Agent):
    
    def setup(self, node=None):
        self.num_requests=0
        self.wakeup_time = datetime.now()
        self.allow_sleep=True
        self.move_time=datetime.now()
        self.check_time=datetime.now() + ONE_MINUTE
        self.node = node
        self.add_behaviour(MoveBehaviour())
        self.add_behaviour(SuspendBehaviour())
        
        """for att in self.node.attributes:
            if str(att.type) == '7d66a5-ea25eaa5bc-bffe39a6a8970943449682fd6b671537':
                self.add_behaviour(AvailabilityBehaviour())"""
        self.resume(allow_sleep=True)
        
    def die(self):
        """ instead of the usual destruction of an agent object an IBA will enter
            it's suspended mode when it dies """
        #super(IBA,self).die()
        self.shutdown=True
        self.go_sleep()
        
    def go_sleep(self,until=None,in_mem=False):
        """ when an agent goes to sleep it's RequestParticipantBehaviour needs to be removed
            since it can't be serialized """
        self.remove_behaviour(self.rpb)
        self.rpb = None
        if until is None:
            self.suspend(in_mem)
        else:
            IBASGlobal.print_message('suspending '+self.shortname+' until '+str(until),1)
            self.suspend_until(until,in_mem)
        
    def resume(self, allow_sleep=False):
        """ resume is called when an IBA is resumed from being suspended """
        self.allow_sleep=allow_sleep
        self.wakeup_time = datetime.now()
        self.move_time = datetime.now() + ONE_MINUTE

        self.rpb = RequestParticipantBehaviour(
            send_response=self._send_response,
            perform_request=self._perform_request,
            send_result=self._send_result,
            cancel=self._cancel
            )
        self.add_behaviour(self.rpb)
    
    def execute(self):
        """ execute is called after an IBA has been moved to another platform """
        self.allow_sleep=True
        self.move_time = datetime.now() + ONE_MINUTE

        self.rpb = RequestParticipantBehaviour(
            send_response=self._send_response,
            perform_request=self._perform_request,
            send_result=self._send_result,
            cancel=self._cancel
            )
        self.add_behaviour(self.rpb)
    
    def _cancel(self):
        IBASGlobal.print_message('IBA cancelling request',2)
    
    def _send_response(self):
        self.move_time = datetime.now() + ONE_MINUTE
        self.num_requests = self.num_requests + 1
        msg = ACLMessage(ACLMessage.INFORM)
        msg.receivers.add(AID('Status Agent'))
        msg.content = self.num_requests
        self.send_message(msg)
        
    def _perform_request(self, request):
        IBASGlobal.print_message('iba performing request '+request,2)
        if request == 'normal':
            res_node = copy.deepcopy(self.node)
            #res_node.statements = res_node.statements[:10] # limit the amount of statements
            #res_node.attributes = res_node.attributes[:10] # limit the amount of attributes
            self.result = res_node
        elif request == 'name':
            # return the first name of the node
            self.result = self.node.get_name(None)
        elif request.startswith('name:'):
            # return the name of the node in the given language
            self.result = self.node.get_name(request.split(':')[1])
        elif request.startswith('nid-name:'):
            # return a tuple containing the nid of the node and it's name in a certain language
            self.result = (self.node.nid,self.node.get_name(request.split(':')[1]))
        elif request == 'nid-name':
            # return a tuple containing the nid of the node and the first name of the node
            self.result = (self.node.nid,self.node.names[0][0])
        elif request.startswith('value-type:'):
            # t consists of the value of the attribute from which the type needs to be determined
            # and a language in which the view agent is currently working
            t = request.split(':')
            self.result = (self._get_value_type(),t[1],t[2])
            IBASGlobal.print_message('iba value type-result '+str(self.result),2)
        
        return True
    
    def _get_value_type(self):
        for att in self.node.attributes:
            if att.type == '26684f-e9c81e478a-5ee972e5a4cb21896e70c4d53b880b97':
                return att.value
        return 'no-type'
    
    def _send_result(self):
        self.last_checked = datetime.now()
        return self.result
    
