"""Spyse Directory Facilitator agent module"""

from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import ReceiveBehaviour
from spyse.core.content.content import ACLMessage
from spyse.core.agents.aid import AID
from spyse.core.platform.constants import Dist
import Pyro.core
import copy
import thread


class DFReceiverBehaviour(ReceiveBehaviour):

    def handle_message(self, msg):
        # Overrides
        content = msg.content
        if content is not None:
            perf = msg.performative
            if perf == ACLMessage.REQUEST:
                self.agent.register_service(msg.sender, content)
                #self.agent.unregisterService(content)
            elif perf == ACLMessage.QUERY_REF:
                agents = self.agent.find_service_providers(content)

                reply = msg.create_reply(ACLMessage.INFORM)
                reply.content = agents

                self.agent.send_message(reply)

            elif perf == ACLMessage.SUBSCRIBE:  # TODO: separate SubscriberParticipantBehaviour ???
                pass
            elif perf == ACLMessage.CANCEL:
                self.agent.unregister_service(msg.sender, content)


# FIXME: Multiple DFs can access the same registry but they don't
# have a common lock

class DF(Agent, Pyro.core.ObjBase):
    """Directory Facilitator agent, aka Yellow Pages"""

    PYRONAME = 'df-server'

    __service_key = 'service'
    __providers_key = 'providers'

    def __init__(self, name, mts, nameserver):
        Pyro.core.ObjBase.__init__(self)
        super(DF, self).__init__(name, mts)
        self.__nameserver = nameserver
 
        # __registry = { title: { service: s, providers: [pp] } }
        # TODO: should enable search for service by template (Service) not just title
        self.__registry = {}
        self.__registry_lock = thread.allocate_lock()

        self.__remote_dfs = set()
        self.__remote_dfs_lock = thread.allocate_lock()
 
    def init_dist(self, dist):
        self.__dist = dist
        if dist == Dist.NONE:
            self.register_service = self.__register_service_basic
            self.unregister_service = self.__unregister_service_basic
            self.find_service = self.__find_service_basic
            self.find_service_providers = self.__find_service_providers_basic
        elif dist == Dist.BCAST_UPDATE:
            self.register_service = self.__register_service_update
            self.unregister_service = self.__unregister_service_update
            self.find_service = self.__find_service_basic
            self.find_service_providers = self.__find_service_providers_basic
        elif dist == Dist.BCAST_RETRIEVE:
            self.register_service = self.__register_service_basic
            self.unregister_service = self.__unregister_service_basic
            self.find_service = self.__find_service_retrieve
            self.find_service_providers = self.__find_service_providers_retrieve
        elif dist == Dist.CENTRAL_SERVER:
            self.register_service = self.__register_service_basic
            self.unregister_service = self.__unregister_service_basic
            self.find_service = self.__find_service_basic
            self.find_service_providers = self.__find_service_providers_basic
            self.daemon.connect(self, DF.PYRONAME)
        elif dist == Dist.CENTRAL_CLIENT:
            self.register_service = self.__register_service_client
            self.unregister_service = self.__unregister_service_client
            self.find_service = self.__find_service_client
            self.find_service_providers = self.__find_service_providers_client
            self.__df_server = Pyro.core.getProxyForURI('PYRONAME://' + DF.PYRONAME)
        else:
            raise Exception("Unrecognized dist")

        if dist == Dist.BCAST_RETRIEVE or dist == Dist.BCAST_UPDATE:
            # We don't have to lock in the init routine
            # but we do need to lock elsewhere.
            self.__remote_dfs = self.__find_others()
            if len(self.__remote_dfs) > 0:
                for df in self.__remote_dfs:
                    df.add_other(self.getProxy())
                if dist == Dist.BCAST_UPDATE:
                    df = self.__remote_dfs.pop()  # Get an arbitrary DF from the list
                    self.__remote_dfs.add(df)     # (and add it back)
                    self.__registry = df.get_registry()  # and get a copy of its registry.

# Commented out because unused
#    def find_other(self):
#        """ find one other DF instance """
#        objs = self.__nameserver.list(":spyse")
#        for obj in objs:
#            if obj[1] == 1 and obj[0].find("/df") != -1:
#                prox = self.__nameserver.resolve(obj[0]).getProxy()
#                if prox.objectID != self.objectGUID:
#                    return prox
    
    def __find_others(self):
        """Find all other DF instances
           Return a set
        """
        others = set()
        objs = self.__nameserver.list(":spyse")
        for obj in objs:
            if obj[1] == 1 and obj[0].find("/df") != -1:
                prox = self.__nameserver.resolve(obj[0]).getProxy()
                if prox.objectID != self.objectGUID:
                    others.add(prox)
        return others
    
    def add_other(self, other):
        """Add a reference to another DF instance.
           (Called by another DF that wishes to publish itself to this DF.)
        """
        self.__remote_dfs_lock.acquire()
        self.__remote_dfs.add(other)
        self.__remote_dfs_lock.release()
        
    def remove_other(self, other):
        """Remove a reference to another DF instance
           (Called by another DF that wishes to cease publishing itself to this DF.)
        """
        self.__remote_dfs_lock.acquire()
        self.__remote_dfs.discard(other)
        self.__remote_dfs_lock.release()
        
    def die(self):
        super(DF, self).die()
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            df.remove_other(self.getProxy())
        self.__remote_dfs_lock.release()

    def setup(self):
        self.add_behaviour(DFReceiverBehaviour())

    def register_service(self, agent_aid, service, localonly=None):
        """Register the given service at the platform. 
        """
        # service must be of class Service
        # TODO: Add leasing for service registration
        pass

    def __register_service_basic(self, agent_aid, service, localonly=None):
        self.__registry_lock.acquire()
        try:
            s = self.__registry[service.title]
        except:
            s = {}
            s[self.__service_key] = service
            s[self.__providers_key] = []
            self.__registry[service.title] = s
        
        for aid in s[self.__providers_key]:
            if aid == agent_aid:
                self.__registry_lock.release()
                return
        s[self.__providers_key].append(agent_aid)
        self.__registry_lock.release()
        print 'Service', service.title, 'registered for agent', agent_aid
    
    def __register_service_update(self, agent_aid, service, localonly=False):
        self.__register_service_basic(agent_aid, service)
        if localonly:
            return
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            df.register_service(agent_aid, service, localonly=True)
        self.__remote_dfs_lock.release()

    def __register_service_client(self, agent_aid, service, localonly=None):
        self.__df_server.register_service(agent_aid, service)

    def unregister_service(self, agent, service, localonly=None):
        """Unregister the given service from the platform. 
        """
        pass

    def __unregister_service_basic(self, agent, service, localonly=None):
        self.__registry_lock.acquire()
        s = self.__registry[service.title]
        if s is not None:
            for prov in s[self.__providers_key]:
                if prov == agent:
                    s[self.__providers_key].remove(prov)
                    break
            if s[self.__providers_key]==[]:
                s = None
        self.__registry_lock.release()
        print 'Service', service.title, 'unregistered for agent', agent
    
    def __unregister_service_update(self, agent, service, localonly=False):
        self.__unregister_service_basic(agent, service)
        if localonly:
            return
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            df.unregister_service(agent, service, localonly=True)
        self.__remote_dfs_lock.release()
    
    def __unregister_service_client(self, agent, service, localonly=None):
        self.__df_server.unregister_service(agent, service)

    def get_registry(self):
        """Return the current registry of all services.
           N.B.: A remote (via Pyro) caller gets a copy of this.
        """
        return self.__registry

    def find_service(self, service, localonly=None):
        """ Find a given service. If the service is present the service will be
            returned or else None will be returned """
        pass
    
    def __find_service_basic(self, service, localonly=False):
        if self.__dist == Dist.CENTRAL_CLIENT:
            return self.__df_server.find_service(agent, service, localonly=True)
        self.__registry_lock.acquire()
        s = self.__registry[service.title]
        self.__registry_lock.release()
        if s is not None:
            return s[self.__service_key]
        if localonly:
            return None
        if self.__dist != Dist.BCAST_RETRIEVE:            
            return None
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            s = df.find_service(service)
            if s is not None:
                self.__remote_dfs_lock.release()
                return s
        self.__remote_dfs_lock.release()
        return None
    
    def __find_service_retrieve(self, service, localonly=False):
        result = self.__find_service_basic(service)
        if result is not None:
            return result
        if localonly:
            return None
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            s = df.find_service(service, False)
            if s is not None:
                self.__remote_dfs_lock.release()
                return s
        self.__remote_dfs_lock.release()
        return None
    
    def __find_service_client(self, service, localonly=None):
        return self.__df_server.find_service(service)

    def find_service_providers(self, service, localonly=None):
        """ Find all agents that offer a certain service """
        pass

    def __find_service_providers_basic(self, service, localonly=None):
        try:
            self.__registry_lock.acquire()
            s = self.__registry[service.title]
            self.__registry_lock.release()
            result = copy.copy(s[self.__providers_key])
            if result is not None:
                return result
            else:
                return []
        except:
            return []
        
    def __find_service_providers_retrieve(self, service, localonly=False):
        result = self.__find_service_providers_basic(service)
        if localonly:
            return result
        self.__remote_dfs_lock.acquire()
        for df in self.__remote_dfs:
            l = df.find_service_providers(service, localonly=True)
            result[:0] = l
        self.__remote_dfs_lock.release()
        return result
        
    def __find_service_providers_client(self, service, localonly=None):
        return self.__df_server.find_service_providers(service)

class Service(object):
    """A service description to be used by DF"""

    # Eventually use some SOAP/WSDL stuff here

    def __init__(self, title, lease=None, ontology=None, language=None, protocol=None):
        self.title = title
        self.lease = lease
        self.ontology = ontology
        self.language = language
        self.protocol = protocol

