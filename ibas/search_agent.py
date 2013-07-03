from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour
from behaviours import DummyBehaviour
from ibas_global import IBASGlobal

from spyse.core.protocols.request import RequestParticipantBehaviour

import Pyro.core
import time

class SearchAgent(Agent,):
    def setup(self, index=None):
        self.__index = index
        self.add_behaviour(RequestParticipantBehaviour(
            send_response=self._send_response,
            perform_request=self._perform_request,
            send_result=self._send_result,
            cancel=self._cancel
        ))
    
    def _cancel(self):
        IBASGlobal.print_message('SA cancelling search',2)
    
    def _send_response(self):
        IBASGlobal.print_message('SA Sending agreed',2)
        
    def _perform_request(self, request):
        self.request_result=[]        
        request = request.split(':')
        if request[0] == "name":
            IBASGlobal.print_message('SA: SEARCHING FOR NAME '+str(request[1]),2)
            self.request_result = self.__index.search_node_by_name(request[1])
        elif request[0] == "att_type":
            IBASGlobal.print_message('SA: SEARCHING FOR ATT_TYPE '+str(request[1]),2)
            self.request_result = self.__index.search_node_by_attribute(request[1],"")
        elif request[0] == "att_value":
            IBASGlobal.print_message('SA: SEARCHING FOR ATT_VALUE '+str(request[1]),2)
            self.request_result = self.__index.search_node_by_attribute("",request[1])
        elif request[0] == "att_type_value":
            IBASGlobal.print_message('SA: SEARCHING FOR ATT_TYPE AND ATT_VALUE '+str(request[1]),2)
            type_value = request[1].split('@')
            self.request_result = self.__index.search_node_by_attribute(type_value[0],type_value[1])
        return True
    
    def _send_result(self):
        IBASGlobal.print_message('SA: sending result',2)
        return self.request_result
