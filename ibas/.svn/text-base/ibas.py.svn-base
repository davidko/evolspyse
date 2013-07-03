from spyse.app.app import App
from spyse.core.platform.platform import Platform
from interface_agent import InterfaceAgent
from iba import IBA
#from iba2 import IBA2
from node import Node, Attribute, Statement
from view_agent import ViewAgent
from view_agent2 import ViewAgent2
from node_index import NodeIndex
from search_agent import SearchAgent
from node_manager_agent import NodeManagerAgent
from status_agent import StatusAgent
from logger_agent import LoggerAgent
from ibas_global import IBASGlobal

import os
import time
import sys
from xml.dom import minidom

class IBAS(App):     
    def run(self, args):  
        try:
            IBASGlobal.verbose_level = int(args[0])
        except:
            IBASGlobal.verbose_level = 0
        index = NodeIndex()        
        index.start()

        self.start_agent(SearchAgent, 'Search Agent', index=index)
        self.start_agent(InterfaceAgent, 'Interface Agent')
        self.start_agent(NodeManagerAgent, 'Node Manager Agent', index=index)
        self.start_agent(LoggerAgent,'Logger Agent')
            
        self.start_agent(ViewAgent, str(Platform.mts.pyrouri)+'ViewAgent')
        
        #data_dir = "nodegathering/n1/"
        data_dir = "nodegathering/n2/"
        #data_dir = "nodegathering/n3/"
        #data_dir = "nodegathering/n4/"
        #data_dir = "nodegathering/n5/"
        
        
        if len(os.listdir('storage')) == 0:
            IBASGlobal.print_message('No stored agents. Parsing XML files again.',0)
            self.start_agent(StatusAgent,'Status Agent')
            files = os.listdir(data_dir)
            for file in files:
                try:
                    xmldoc = minidom.parse(data_dir+file)
                    iba_node = Node()
                    self._parse_xml(xmldoc,iba_node)
                    name = self.create_agent(IBA, str(iba_node.nid), node=iba_node)
                    #name = self.start_agent(IBA, str(iba_node.nid), node=iba_node)
                    #time.sleep(0.2)
                    index.index_node(iba_node)
                    
                except:
                    IBASGlobal.print_message("## error while creating iba from:"+file+"##",0)
                    
            self.invoke_all_agents()
        
        IBASGlobal.print_message('########### IBAS STARTED #############',0)
    
    def _parse_xml(self, xmldoc, iba_node):
        for node in xmldoc.firstChild.childNodes:
            if node.nodeName == 'NID' and iba_node.nid=="":
                iba_node.nid = node.firstChild.data.strip()
            elif node.nodeName == 'SNENames':
                self._handle_names(node, iba_node)
            elif node.nodeName == 'SNEStatements':
                self._handle_statements(node, iba_node)
            elif node.nodeName == 'SNEAttributes':
                self._handle_attributes(node, iba_node)
    
    def _handle_names(self, xml_node, iba_node):
        for node in xml_node.childNodes:
            if node.nodeName == 'SNEName':
                iba_node.names.append((node.firstChild.data.strip(), node.getAttribute('languageNID')))
    
    def _handle_statements(self, xml_node, iba_node):
        for node in xml_node.childNodes:
            if node.nodeName == 'SNEStatement':
                stat = Statement()
                stat.subject = iba_node.nid
                stat.predicate = node.getAttribute('predicateNID')
                stat.object = node.getAttribute('objectNID')
                for cnode in node.childNodes:
                    if cnode.nodeName == 'SNEAttributes':
                        self._handle_attributes(cnode, stat)
                iba_node.statements.append(stat)
    
    def _handle_attributes(self, xml_node, parent):
        for node in xml_node.childNodes:
            if node.nodeName == 'SNEAttribute':
                att = Attribute()
                att.type = node.getAttribute('typeNID')
                att.value = node.firstChild.data.strip()
                parent.attributes.append(att)
                for node2 in node.childNodes:
                    if node2.nodeName == 'SNEAttributes':
                        self._handle_attributes(node2, att)

if __name__ == "__main__":
    IBAS()