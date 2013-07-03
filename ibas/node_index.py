import PyLucene
from PyLucene import Field
from spyse.core.platform.platform import Platform

import thread
import os
import time
from Queue import Queue

from ibas_global import IBASGlobal

COLUMN_NID                 = "nid"
COLUMN_NODE_STATUS         = "cloneStatus"
COLUMN_OBJECT              = "object"
COLUMN_NAME                = "name"
COLUMN_ATTRIBUTE_TYPE_NID  = "attributeTypeNid"
COLUMN_ATTRIBUTE_VALUE     = "attributeValue"
COLUMN_PREDICATE_NID       = "predicateNid"
COLUMN_OLD_NID             = "oldNid"
COLUMN_OBJECT_NID          = "objectNid"

# The NodeIndex is run in a PyLucene.PythonThread to avoid any synchronization errors
# Nodes that should be added to the index need to be appended to the 'nodes' Queue
# Search requests should be added to the 'requests' Queue
class NodeIndex(PyLucene.PythonThread):
#class NodeIndex(object):
    def __init__(self):
        self.__lock = thread.allocate_lock()
        self.__reqlock = thread.allocate_lock()
        super(NodeIndex,self).__init__()
        self.searcher = None
        self.__modified = False
        self.nodes = Queue()
        self.requests = Queue()
        self.result = None
        self.count = 0
    
    def run(self):
        while Platform.running:
            try:
                new_node = self.nodes.get(False)
                try:
                    self.index_node(new_node)
                    self.__modified = True
                except:
                    self.nodes.put(new_node)
            except:
                pass
            
            try:
                req = self.requests.get(False)
                if req is not None and req[0] == 'name':
                    self.result = self.search_node_by_name2(req[1])
                elif req is not None and req[0] == 'attribute':
                    self.result = self.search_node_by_attribute2(req[1], req[2])
            except:
                pass
            time.sleep(0.5)
    
    def index_node(self, iba_node):
        self.delete_node(iba_node.nid)
        create = len(os.listdir('index')) == 0
        analyzer = PyLucene.StandardAnalyzer();
        writer =  PyLucene.IndexWriter("index",analyzer,create);
        
        writer.addDocument(self._document_node(iba_node))
        writer.close()
        self.count = self.count + 1
        
    def delete_node(self, nid):
       try:
           index_present = len(os.listdir('index')) > 0
           if index_present:
               reader = PyLucene.IndexReader.open("index");
               term = PyLucene.Term(COLUMN_NID, nid)
               if reader.termDocs(term) != None:
                   reader.deleteDocuments(term)
               reader.close();
       except:
           IBASGlobal.print_message("Error while deleting document from Lucene with nid "+str(nid),0)
    
    def _document_node(self, iba_node):
        d = PyLucene.Document()
        # Index the NID
        d.add(Field(COLUMN_NID, iba_node.nid, Field.Store.YES, Field.Index.UN_TOKENIZED ))
        
        # Index the Names
        for name in iba_node.names:
            d.add(Field(COLUMN_NAME, name[0],Field.Store.NO, Field.Index.TOKENIZED))
            
        # Index the Attributes
        for att in iba_node.attributes:
            # allowing search for nodes having a particular attribute type            
            d.add(Field(COLUMN_ATTRIBUTE_TYPE_NID, att.type, Field.Store.NO, Field.Index.TOKENIZED))
            # allowing the search of nodes with any attribute having a particular value
            d.add(Field(COLUMN_ATTRIBUTE_VALUE, att.value, Field.Store.NO, Field.Index.TOKENIZED))
            # allowing the search of nodes having aparticular attribute with a particular value
            d.add(Field(COLUMN_ATTRIBUTE_TYPE_NID, att.value, Field.Store.NO, Field.Index.TOKENIZED))
            
        # Index the Statements
        for stat in iba_node.statements:
            for att in stat.attributes:
                # allowing the search of nodes have any predicate with the specified attribute type
                d.add(Field(COLUMN_PREDICATE_NID + COLUMN_ATTRIBUTE_TYPE_NID,att.type, Field.Store.NO, Field.Index.TOKENIZED))
                # allowing the search of nodes having the specified predicate with the specified attribute type of any value
                d.add(Field(stat.predicate + COLUMN_ATTRIBUTE_TYPE_NID,att.type, Field.Store.NO, Field.Index.TOKENIZED))
                # allowing the search of nodes having the specified predicate with any attribute type and any value
                d.add(Field(COLUMN_PREDICATE_NID, stat.predicate, Field.Store.NO, Field.Index.TOKENIZED))
                
                # allowing the search of nodes have any predicate with any attribute type of the specified value
                d.add(Field(COLUMN_PREDICATE_NID + COLUMN_ATTRIBUTE_TYPE_NID, att.value, Field.Store.NO, Field.Index.TOKENIZED))
                # allowing the search of node having any predicate with the specified attribute type and value
                d.add(Field(COLUMN_PREDICATE_NID + att.type, att.value, Field.Store.NO, Field.Index.TOKENIZED))
                # allowing the search of nodes having the specified predicate with any attribute type and the specified value
                d.add(Field(stat.predicate + COLUMN_ATTRIBUTE_TYPE_NID, att.value, Field.Store.NO, Field.Index.TOKENIZED))
                # allowign the search of nodes having a specified predicate and attribute type and value
                d.add(Field(stat.predicate + att.type, att.value, Field.Store.NO, Field.Index.TOKENIZED))
        
        return d
    
    def search_node_by_name(self, name):
        self.requests.put(('name',name))
        while self.result is None:
            time.sleep(0.3)
        res = self.result
        self.result = None

        return res
    
    def search_node_by_name2(self, name):
        if self.searcher is None:
            self.searcher = PyLucene.IndexSearcher("index")

        query = PyLucene.QueryParser(COLUMN_NAME, PyLucene.StandardAnalyzer()).parse(name)
        hits = self.searcher.search(query)
        result = self.hits_to_list(hits)

        return result
    
    def search_node_by_attribute(self, att_type, att_value):
        self.requests.put(('attribute',att_type,att_value))
        while self.result is None:
            time.sleep(0.3)
        res = self.result
        self.result= None
        return res
    
    def search_node_by_attribute2(self, att_type, att_value):
        if self.searcher is None:
            self.searcher = PyLucene.IndexSearcher("index")
        
        analyzer =  PyLucene.StandardAnalyzer()    
        
        if att_type != "" and att_value == "":
            parser = PyLucene.QueryParser(COLUMN_ATTRIBUTE_TYPE_NID, analyzer)
            query = parser.parse(att_type)
        elif att_type == "" and att_value != "":
            parser = PyLucene.QueryParser(COLUMN_ATTRIBUTE_VALUE, analyzer)
            query = parser.parse(att_value)
        elif att_type != "" and att_value != "":
            parser = PyLucene.QueryParser(COLUMN_ATTRIBUTE_VALUE, analyzer)
            query = parser.parse(COLUMN_ATTRIBUTE_TYPE_NID+":"+att_type+" AND "+att_value)
            
        hits = self.searcher.search(query)
        result = self.hits_to_list(hits)
       
        return result;
            
        
    def hits_to_list(self, hits):
        nids = []
        for hit in hits:
            nid = hit.get("nid");
            nids.append(nid)
        return nids;