from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.protocols.request import RequestInitiatorBehaviour
from spyse.core.platform.df import Service
from spyse.core.content.content import ACLMessage

from behaviours import DummyBehaviour
from ibas_global import IBASGlobal
import Pyro.core
import time

class InterfaceAgentBehaviour(Behaviour):
    def action(self):
        msg = self.agent.get_message()
        if msg:
            pass
            """
            content = self.__cm.extractContent(msg)
            perf = msg.performative
            if perf==ACLMessage.INFORM:    # if we have received a list from the DF
                    p=content[0]        # take the first one out of the list
            """

class InterfaceAgent(Agent, Pyro.core.ObjBase):
    def setup(self, index=None):
        Pyro.core.ObjBase.__init__(self)
        Platform.daemon.connect(self,'InterfaceAgent')
        self.add_behaviour(DummyBehaviour())
        self.__index = index
        
    def echo(self, s):
        return s
    
    def get_agent_count(self):
        return self.mts.ams.getRegistryCount()
    
    def get_containers_info(self):
        return self.mts.ams.get_containers_info()
    
    def get_num_requests(self):
        msg = ACLMessage(ACLMessage.REQUEST)
        msg.receivers.add(AID('Status Agent'))
        self.send_message(msg)
        res = self.get_message()
        while res is None:
            res = self.get_message()
            time.sleep(0.1)
        return res.content
    
    def get_log(self):
        msg = ACLMessage(ACLMessage.REQUEST)
        msg.receivers.add(AID('Logger Agent'))
        self.send_message(msg)
        res = self.get_message()
        while res is None:
            res = self.get_message()
            time.sleep(0.1)
        return res.content
    
    def add_node(self, path):
        IBASGlobal.print_message('IA: Add Node: '+str(path),1)
        self.node_rep = None
        
        self.add_behaviour(RequestInitiatorBehaviour(
            store=AID('Node Manager Agent'),
            request=path,
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform_view,
            handle_inform_done=self._handle_inform_done_view,
            handle_failure=self._handle_failure,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))
        
        while self.node_rep == None:
            time.sleep(0.5)
        
        res = self.node_rep
        self.node_rep = None
        return res
    
    def view_node(self, nid, language):
        IBASGlobal.print_message('IA: View Node: '+str(nid)+' language '+str(language), 1)
        self.node_rep = None
        aid = self.mts.ams.find_agent(nid)
        if aid is None:
            aid = self.aid
        pyroloc = str(aid.addresses[0])
        self.add_behaviour(RequestInitiatorBehaviour(
            store=AID(pyroloc+'ViewAgent'),
            request=str(nid)+' '+str(language),
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform_view,
            handle_inform_done=self._handle_inform_done_view,
            handle_failure=self._handle_failure,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))
        
        while self.node_rep == None:
            time.sleep(0.5)
        
        res = self.node_rep
        self.node_rep = None
        return res
        
    def _handle_inform_view(self, content):
        IBASGlobal.print_message('Node representation received',2)
        self.node_rep = content
        
    def _handle_inform_done_view(self, content):
        IBASGlobal.print_message('Node could not be found',1)
        self.node_rep = "Node could not be found"
        
    def get_nid_name(self, nid, language):
        IBASGlobal.print_message('IA: GET NAME FOR '+str(nid)+' language' +str(language),2)
        self.search_result = None
        
        self.add_behaviour(RequestInitiatorBehaviour(
            store=AID(str(nid)),
            request='name:'+language,
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform,
            handle_inform_done=self._handle_inform_done,
            handle_failure=self._handle_failure,
            handle_no_participant=self._handle_no_participant,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))
        
        while self.search_result is None:
            time.sleep(0.1)
        res = self.search_result
        self.search_result = None
        return res
        
    def search_node_by_name(self, name):
        IBASGlobal.print_message('IA: SEARCH FOR '+str(name)+' INITIATED',1)
        self.search_result = None
        
        self.add_behaviour(RequestInitiatorBehaviour(
            store=AID('Search Agent'),
            request='name:'+name,
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform,
            handle_inform_done=self._handle_inform_done,
            handle_failure=self._handle_failure,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))
        
        while self.search_result is None:
            time.sleep(0.5)
        res = self.search_result
        self.search_result = None
        return res
    
    def search_node_by_attribute(self, att_type, att_value):
        IBASGlobal.print_message('IA: SEARCH FOR ATT_TYPE '+str(att_type)+' AND VALUE WITH '+str(att_value),1)
        self.search_result = None
        
        if att_type != "" and att_value == "":
            request='att_type:'+att_type
        elif att_type == "" and att_value != "":
            request='att_value:'+att_value
        else:
            request='att_type_value:"'+att_type+'"#"'+att_value+'"'
        
        self.add_behaviour(RequestInitiatorBehaviour(
            store=AID('Search Agent'),
            request=request,
            handle_response=self._handle_response,
            handle_agree=self._handle_agree,
            handle_refuse=self._handle_refuse,
            handle_inform=self._handle_inform,
            handle_inform_done=self._handle_inform_done,
            handle_failure=self._handle_failure,
            cancel=self._cancel,
            check_cancel=self._check_cancel
        ))
        
        while self.search_result is None:
            time.sleep(0.5)
        res = self.search_result
        self.search_result = None
        return res
    
    def _check_cancel(self):
        return False
    
    def _handle_response(self):
        IBASGlobal.print_message('IA: handling response',2)
    
    def _handle_agree(self):
        IBASGlobal.print_message('IA: handling agreed',2)
        
    def _handle_refuse(self):
        IBASGlobal.print_message('IA: handling refuse',2)
    
    def _handle_failure(self):
        IBASGlobal.print_message('IA: handling failure',2)
        
    def _handle_no_participant(self,participant):
        self.search_result=participant.shortname
        IBASGlobal.print_message('IA: handling no participant',2)
        
    def _cancel(self):
        IBASGlobal.print_message('IA: cancelling search',2)
    
    def _handle_inform_done(self, content):
        IBASGlobal.print_message('IA: NO AGENTS FOUND',2)
        self.search_result = "no agents found"
    
    def _handle_inform(self, content):
        IBASGlobal.print_message('IA: FOUND '+str(content),2)
        self.search_result = content
