from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.platform.df import Service
from behaviours import DummyBehaviour, RegisterServiceBehaviour
from ibas_global import IBASGlobal

from spyse.core.protocols.request import RequestParticipantBehaviour, RequestInitiatorBehaviour

import Pyro.core
import time
import thread

NODE_KEY = "node_key"
NID_KEY = "nid_key"
NAME_KEY = "name_key"
ATTRIBUTE_KEY = "attribute_key"
ATTRIBUTE_VALUE_KEY = "attribute_value_key"
STATEMENT_KEY = "statement_key"
NID_DICT_KEY = "nid_dict_key"

RESTRICTED_TO = "461380-103019f05e8-6af97b9f15b8e19997718d8248d98157"
NODE_IDENTIFIER = "26684f-e9c81d0a38-5ee972e5a4cb21896e70c4d53b880b97"

REQUEST_NOTHING = 0
REQUEST_NODE = 1
REQUEST_INFO = 2
REQUEST_WAIT = 3
REQUEST_DONE = 4
       
class ViewAgent(Agent):
    def setup(self):
        self.__lock = thread.allocate_lock()
        self.status = REQUEST_NOTHING
        self.add_behaviour(RegisterServiceBehaviour(args=Service('View')))
        
        self.add_behaviour(RequestParticipantBehaviour(
            send_response=self._send_response,
            perform_request = self._perform_request,
            send_result=self._send_result,
            cancel=self._cancel
        ))
        
    def _cancel(self):
        IBASGlobal.print_message('VA cancelling view request',2)
    
    def _send_response(self):
        self.status = REQUEST_NODE
        self.name_requests=0
        self.name_responses=0
        self.value_type_requests=0
        self.value_type_responses=0
        self.data = {}
        self.data[NODE_KEY] = None
        self.data[NID_DICT_KEY] = {}    # contains names of certain nids
        IBASGlobal.print_message('VA Sending agreed',2)
        
    def _perform_request(self, request):
        request = request.split(' ')

        if self.status == REQUEST_NODE:
            IBASGlobal.print_message('VA: trying to contact '+str(request[0]),2)
            self.add_behaviour(RequestInitiatorBehaviour(
                store=AID(str(request[0])),
                request="normal",
                handle_no_participant=self._handle_no_participant,
                handle_response=self._handle_response,
                handle_agree=self._handle_agree,
                handle_inform=self._handle_inform,
                handle_inform_done=self._handle_inform_done,
                check_cancel=self._check_cancel
            ))
            self.status = REQUEST_INFO
        elif self.status == REQUEST_INFO:
            if self.data[NODE_KEY]:
                for att in self.data[NODE_KEY].attributes:
                    self._handle_attribute(att,request[1])
                for stat in self.data[NODE_KEY].statements:
                    restricted=False
                    for att in stat.attributes:
                        if str(att.type) == RESTRICTED_TO:
                            restricted = True
                            
                    if restricted:
                        self.data[NID_DICT_KEY][stat.predicate] = 'Restricted'
                        self.data[NID_DICT_KEY][stat.object] = 'Restricted'
                    else:
                        self._request_nid_name(stat.predicate,request[1])
                        self._request_nid_name(stat.object,request[1])
                        for att in stat.attributes:
                            self._handle_attribute(att,request[1])    
                for name in self.data[NODE_KEY].names:
                    self._request_nid_name(name[1],request[1])
                self.status = REQUEST_WAIT
        elif self.status == REQUEST_WAIT:
            if self.name_responses >= self.name_requests and \
                    self.value_type_responses >= self.value_type_requests:
                return True
        
        return False
    
    def _handle_attribute(self, attribute, language):
        self.__lock.acquire()
        self.value_type_requests = self.value_type_requests + 1
        self.__lock.release()
        self._request_nid_name(attribute.type, language)
        #self._request_nid_name(attribute.value, language)
        value = attribute.value
        if isinstance(value,unicode): 
            value = value.encode("utf-8")
            
        self.add_behaviour(RequestInitiatorBehaviour(
                        store=AID(str(attribute.type)),
                        request='value-type:'+str(value)+":"+str(language),
                        handle_no_participant=self._handle_no_participant_value_type,
                        handle_inform=self._handle_inform_value_type,
                        check_cancel=self._check_cancel
                        ))
        
        for att in attribute.attributes:
            self._handle_attribute(att,language)
            
    def _handle_no_participant_value_type(self, result):
        self.__lock.acquire()
        self.value_type_responses = self.value_type_responses + 1
        self.__lock.release()
    
    def _handle_inform_value_type(self, result):
        #result = result.split(":")
        if result[0] == NODE_IDENTIFIER:
            self._request_nid_name(result[1], result[2])
        
        self.__lock.acquire()
        self.value_type_responses = self.value_type_responses + 1
        self.__lock.release()
    
    def _request_nid_name(self, nid, language):
        IBASGlobal.print_message('VA requesting nid-name '+str(nid),2)
        try:
            nid = str(nid)
        except:
            return
        self.__lock.acquire()
        if self.data[NID_DICT_KEY].has_key(nid): 
            self.__lock.release()
            return
        self.data[NID_DICT_KEY][nid] = None
        self.name_requests = self.name_requests + 1
        self.__lock.release()
        self.add_behaviour(RequestInitiatorBehaviour(
                        store=AID(str(nid)),
                        request='nid-name:'+str(language),
                        handle_no_participant=self._handle_no_participant_name,
                        handle_agree=self._handle_agree,
                        handle_inform=self._handle_inform_name,
                        handle_inform_done=self._handle_inform_done_name,
                        check_cancel=self._check_cancel
                        ))
        return
    
    def _send_result(self):
        IBASGlobal.print_message('VA: Node representation created',2)
        return self.data
        
    def _check_cancel(self):
        return False
    
    def _handle_response(self):
        IBASGlobal.print_message('VA handling response',2)
        
    def _handle_agree(self):
        IBASGlobal.print_message('VA handling agree',2)
        
    def _handle_no_participant(self, aid):
        IBASGlobal.print_message('VA handle no participant',2)
        self.data[NODE_KEY] = None
    
    def _handle_inform(self, node):
        IBASGlobal.print_message('VA handle inform',2)
        self.data[NODE_KEY] = node
        
    def _handle_inform_done(self, content):
        self.node_rep = ""
        
    def _handle_no_participant_name(self, aid):
        IBASGlobal.print_message('va handling no participant nid-name '+str(aid),2)
        self.__lock.acquire()
        self.name_responses = self.name_responses + 1
        self.data[NID_DICT_KEY][aid.shortname] = "Unknown"
        self.__lock.release()
        
    def _handle_inform_name(self, nidname):
        IBASGlobal.print_message('va handling inform nid-name '+str(nidname),2)
        self.__lock.acquire()
        self.name_responses = self.name_responses + 1
        self.data[NID_DICT_KEY][nidname[0]] = nidname[1]
        self.__lock.release()
        #print self.data[NID_DICT_KEY]
    
    def _handle_inform_done_name(self, node):
        IBASGlobal.print_message('va handling inform-done-name',2)
                
                