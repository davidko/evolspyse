from spyse.core.agents.agent import Agent
from spyse.core.platform.platform import Platform
from spyse.core.behaviours.behaviours import Behaviour
from behaviours import DummyBehaviour

from spyse.core.protocols.request import RequestParticipantBehaviour
from iba import IBA
from node import Node, Attribute, Statement
from ibas_global import IBASGlobal

import Pyro.core
import os
import urllib2
import time
import thread
import zipfile
from xml.dom import minidom

class NodeManagerAgent(Agent,):
    def setup(self, index=None):
        self.__index = index
        self.__processing_nids= []
        self.__processing_nids_lock = thread.allocate_lock()
        self.__zip_lock = thread.allocate_lock() # only 1 zip file can be handled at a time
        self.add_behaviour(RequestParticipantBehaviour(
            send_response=self._send_response,
            perform_request=self._perform_request,
            send_result=self._send_result,
            cancel=self._cancel
        ))
    
    def _cancel(self):
        IBASGlobal.print_message('NMA cancelling search',2)
    
    def _send_response(self):
        IBASGlobal.print_message('NMA Sending agreed',2)
    
    def __add_zip(self, request):
        self.__zip_lock.acquire()
        zipobj = zipfile.ZipFile(request)
        for name in zipobj.namelist():
            try:
                out_name = name.split('/')
                out_name = out_name[len(out_name)-1]
                outfile = open('tmp/'+out_name, 'w')
                outfile.write(zipobj.read(name))
                outfile.close()
                self.__add_node('tmp/'+out_name)
                os.remove('tmp/'+out_name)
                time.sleep(0.2)
            except:
                self.result.append('Error while reading xml from zip: '+name)
        self.__zip_lock.release()
        return True
        
    def __add_node(self, request):
        self.__processing_nids_lock.acquire()
        nid = request
        
        if request.endswith(".xml"):
            nid = request.strip('.xml')
            
        if nid in self.__processing_nids:
            self.result.append('Error already adding '+nid)
            self.__processing_nids_lock.release()
            return True
        
        self.__processing_nids.append(nid)
        self.__processing_nids_lock.release()
        if request.endswith(".xml"):        
                self.__add_node_xml(request)
        else:
                self.__add_node_sne(nid)
                
        self.__processing_nids_lock.acquire()
        self.__processing_nids.remove(nid)    
        self.__processing_nids_lock.release()
        
        return True
        
    
    def __add_node_sne(self, nid):
        try:
            url = "http://pc50002945:8045/sne/xml/getXmlNode?nid="+str(nid)
            xml_file = urllib2.urlopen(url)
            xmldoc = minidom.parse(xml_file)
            self.iba_node = Node()
            self._parse_xml(xmldoc,self.iba_node)
        except:
            self.result.append('Error while parsing XML for node: '+nid)
            return

        try:
            self.mts.ams.start_agent(IBA, str(self.iba_node.nid), node=self.iba_node)
            self.result.append(nid+" IBA created")
        except:
            self.result.append('Error while starting new IBA:'+self.iba_node.nid)
            return            
            
        try:
            self.__index.nodes.put(self.iba_node)
            IBASGlobal.print_message('Added node to index '+str(nid),2)
        except:
            self.result.append('Error while adding new node to index:'+self.iba_node.nid)
    
    def __add_node_xml(self, xml_path):
        try:
            xmldoc = minidom.parse(xml_path)
            self.iba_node = Node()
            self._parse_xml(xmldoc,self.iba_node)
        except:
            self.result.append('Error while parsing XML:'+xml_path)
            return
            
        try:
            self.__index.nodes.put(self.iba_node)
        except:
            self.result.append('Error while adding new node to index:'+self.iba_node.nid)
            return

        try:
            name = self.mts.ams.create_agent(IBA, str(self.iba_node.nid), node=self.iba_node)
            if name is not None:
                self.mts.ams.invoke_agent(name)
        except:
            self.result.append('NMA: error while starting new IBA:'+self.iba_node.nid)
        
    def _perform_request(self, request):
        IBASGlobal.print_message('NMA: request '+str(request),2)
        self.result = []
        if request.endswith('.zip'):
            self.__add_zip(request)
        else:
            self.__add_node(request)
        
        self.result.append('New node(s) added.')
        return True
    
    def _send_result(self):
        IBASGlobal.print_message('NMA: sending result',2)
        return self.result
    
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
