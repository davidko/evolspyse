"""Spyse Agent Management Service agent module"""

# The Agent Management Service agent creates agents and
# destroys them.  There is one AMS for each platform.

# We assume that other AMS don't get created or destroyed
# while we are, e.g., iterating over our list of them.
# FIXME: Don't assume this

# http://www.fipa.org/specs/fipa00023/SC00023K.html

import os
import thread
import threading
from collections import deque
import copy
import logging
import random
import time
import cPickle as pickle
import Pyro4.core
from datetime import datetime

from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.platform.constants import Dist, ThreadMeth, AgentState
from spyse.core.platform.threadpool import ThreadPool


class WakeupBehaviour(Behaviour):
    def action(self):
        self.agent.wakeup_check()


class AMSReceiverBehaviour(Behaviour):
    def setup(self):
        pass

    def action(self):
        msg = self.agent.get_message()
        if msg:
            item = msg.content
            if item is None:
                self.set_done()
            else:
                self.sleep(random.randint(10, 100) / 1000.0)
                print self.agent.name, "task", item, "finished"
        # Do something useful with received messages, e.g. create agents ;-)


class AMS(Agent):
    """Agent Management Service agent"""
    
    # Threading modes
    # Normal : Every agent runs in a different thread
    # Pool   : A thread pool processes the agents
    # Off    : All agents are run together in one seperate thread
    THREADS_NORMAL = 'NORMAL'
    THREADS_POOL = 'POOL'
    THREADS_OFF = 'OFF'
    
    PYRONAME = 'ams-server'
    AGENT_STORAGE = 'storage/'

    # maybe use ZODB for persistence

    def __init__(self, pyro4daemon, nameserver, hap, mts, threadmeth, poolsize):
        self.__aid = AID(shortname='AMS', hap=hap)
        super(AMS, self).__init__(name=self.__aid, mts=mts)
        self.daemon = pyro4daemon

        # Every known agent (or AID if it's remote) is stored by name in the registry.
        # Each runnable (and therefore local) agent is, additionally, stored in the runnable_agents dictionary.
        # Each suspended (and therefore not runnable, but nevertheless local) agent is stored by shortname in the suspended_shortnames list.
        # The suspended_to_mem dictionary contains the agents that are suspended but should remain in memory so they can be resumed faster.

        self.__registry = {}  # agent or AID by name
        self.__runnable_agents = {}  # by name
        self.__suspended_shortnames = []
        self.__suspended_to_mem = {}
        # This lock protects the registry, runnable_agents, suspended_shortnames, suspended_to_mem
        # and agent run state attributes
        self.__lock = thread.allocate_lock()

        # Wakeup times are added to the wakeup_times list. Additionally the wakeup times are
        # added to the wakeup_dict_times. The time will be used as key and the value will be a 
        # list of agents that need to be waked. In wakeup_dict_agents the shortname is used as key
        # and the time as value. The wakeup_lock will protect all these attributes.
        self.__waking = True
        self.__wakeup_dict_times = {}
        self.__wakeup_dict_agents = {}
        self.__wakeup_times = []
        self.__wakeup_lock = thread.allocate_lock()
        self.__nameserver = nameserver
        self.__hap = hap
        self.__running = False 

        # remote_amses contains proxies to all other AMSes that are running.
        # The lock is used to protect access to remote_amses itself and to each of the
        # proxies in it.  (We could have a distinct lock per proxy, but that would
        # complicate things.)
        self.__remote_amses = set()
        self.__remote_amses_lock = thread.allocate_lock()
        self.__ams_server = None

        try:
            self.__suspended_shortnames = os.listdir("storage")
            for suspended_shortname in self.__suspended_shortnames:
                aid = AID(shortname=suspended_shortname, hap=hap)
                self.__registry[aid.name] = aid
        except:
            pass

        self.poolsize = poolsize
        self.pool = None

        if threadmeth == ThreadMeth.OFF:
            self.invoke_agent = self.__invoke_agent_nothread
        elif threadmeth == ThreadMeth.POOL:
            self.invoke_agent = self.__invoke_agent_pool
        elif threadmeth == ThreadMeth.NORMAL:
            self.invoke_agent = self.__invoke_agent_thread
        else:
            print "threadmeth is", threadmeth
            print "threadmeth == ThreadMeth.OFF:", threadmeth == ThreadMeth.OFF
            print "threadmeth == ThreadMeth.POOL:", threadmeth == ThreadMeth.POOL
            print "threadmeth == ThreadMeth.NORMAL:", threadmeth == ThreadMeth.NORMAL
            raise Exception("Unrecognized threadmeth")

        self.__load_wakeup_list()
        self.add_behaviour(WakeupBehaviour(self))
        self.add_behaviour(AMSReceiverBehaviour(self))
        self.state = AgentState.INITIATED
        
        self.__register_agent_local(self)
        self.invoke_agent(self.name)

    def init_dist(self, dist):
        if dist == Dist.NONE:
            self.register_agent = self.__register_agent_basic
            self.unregister_agent = self.__unregister_agent_basic
            self.find_agent = self.__find_agent_basic
            # We should still register the ams to the name server
            # if possible, in case agents are interested in finding amses
            self.__register_to_nameserver()
        elif dist == Dist.BCAST_UPDATE:
            self.register_agent = self.__register_agent_update
            self.unregister_agent = self.__unregister_agent_update
            self.find_agent = self.__find_agent_basic
            self.__register_to_nameserver()
        elif dist == Dist.BCAST_RETRIEVE:
            self.register_agent = self.__register_agent_retrieve
            self.unregister_agent = self.__unregister_agent_retrieve
            self.find_agent = self.__find_agent_retrieve
            self.__register_to_nameserver()
        elif dist == Dist.CENTRAL_SERVER:
            self.register_agent = self.__register_agent_basic
            self.unregister_agent = self.__unregister_agent_basic
            self.find_agent = self.__find_agent_basic
            self.__register_to_nameserver(AMS.PYRONAME)
        elif dist == Dist.CENTRAL_CLIENT:
            self.register_agent = self.__register_agent_client
            self.unregister_agent = self.__unregister_agent_client
            self.find_agent = self.__find_agent_client
            self.__ams_server = self.__find_server()
            self.__register_to_nameserver()
        else:
            raise ValueError("Unrecognized dist")

        if dist != Dist.NONE:
            # We don't have to lock __remote_amses in the init routine
            # but we do need to lock it elsewhere.
            self.__remote_amses = self.__find_others()
            if len(self.__remote_amses) > 0:
                if dist == Dist.BCAST_RETRIEVE or dist == Dist.BCAST_UPDATE:
                    for ams in self.__remote_amses:
                        ams.add_other(self.getProxy())
                if dist == Dist.BCAST_UPDATE:
                    ams = self.__remote_amses.pop()  # Get an arbitrary AMS
                    self.__remote_amses.add(ams)     # and add it back
                    aids = ams.find_agents()
                    for aid in aids:
                        if aid.shortname != 'DF':
                            self.register_agent(aid, localonly=True)

    def __find_server(self):
        uri = self.__nameserver.lookup(AMS.PYRONAME)
        return Pyro4.Proxy(uri)

    def __find_others(self):
        """Find all other AMS instances.
           Returns a set.
        """
        others = set()
        objs = self.__nameserver.list()
        objs = dict(map(lambda (k, v): (str(k), v), objs.iteritems()))
        for key, obj in objs.items():
            if key.startswith('spyse:') and key.endswith('ams'):
                others.add(Pyro4.Proxy(obj))
        return others

    def __register_to_nameserver(self, name=None):
        uri = self.daemon.register(self)
        if name is None:
            name = 'spyse:'+self.__hap.name+'/ams'
        try:
            self.__nameserver.register(name, uri)
        except:
            pass

    def find_others(self):
        return self.__find_others()
    
    def add_other(self, other):
        """Add a reference to another AMS instance.
           (Called by another AMS that wishes to publish itself to this AMS.)
        """
        self.__remote_amses_lock.acquire()
        self.__remote_amses.add(other)
        self.__remote_amses_lock.release()
        
    def remove_other(self, other):
        """Remove a reference to another AMS instance
           (Called by another AMS that wishes to cease publishing itself to this AMS.)
        """
        self.__remote_amses_lock.acquire()
        self.__remote_amses.discard(other)
        self.__remote_amses_lock.release()

    def setup(self):
        pass

    def __get_population(self):
        self.__lock.acquire()
        pop = len(self.__registry)
        self.__lock.release()
        return pop

    population = property(__get_population, None, None, "population")

# Commented out because unused
#    def resume_all(self):
#        """Resume all suspended agents"""
#        files = os.listdir(AGENT_STORAGE)
#        for f in files:
#            self.resume_agent(i.name)
        
    def __resume_agent(self, shortname):
        """Resume the agent with the given name. The state will be
           changed and the agent will be invoked again and returned.
           If the agent isn't suspended then do nothing and return None.
        """
        self.__lock.acquire()
        if not shortname in self.__suspended_shortnames:
            self.__lock.release()
            return None
        try:
            #if not shortname in self.__suspended_to_mem:
            #    return
            self.__wakeup_lock.acquire()
            try:
                t = self.__wakeup_dict_agents.pop(shortname)
                self.__wakeup_dict_times[t].remove(shortname)
            except: 
                pass

            self.__wakeup_lock.release()
            self.__save_wakeup_list()
            
            agent = None
            fromfile = False
            
            if shortname in self.__suspended_to_mem:
                agent = self.__suspended_to_mem[shortname]
            else:
                f = open(AMS.AGENT_STORAGE + shortname, 'r')
                agent = pickle.load(f)
                f.close()
                fromfile = True
                
            if agent.state != AgentState.SUSPENDED:
                print 'Agent', shortname, 'cannot be resumed because it is not suspended.'
            else:
                temp_aid = AID(shortname=shortname, hap=self.__hap)
                agent.aid.name = temp_aid.name
                agent.aid.addresses = [self.mts.pyrouri]
                agent.mts = self.mts
                self.__registry[agent.name] = agent
                self.__suspended_shortnames.remove(shortname)
                self.__runnable_agents[agent.name] = agent
                self.__lock.release()
                agent.resume()
                self.invoke_agent(agent.name)
                
                if fromfile:
                    os.remove(AMS.AGENT_STORAGE + shortname)
                else:
                    del self.__suspended_to_mem[shortname]
                return agent
        except:
            print shortname, 'could not be resumed'
    
    def suspend_agent(self, name, in_mem=False):
        self.__lock.acquire()
        known = name in self.__registry
        if not known:
            self.__lock.release()
            print 'Agent', name, 'not suspended because it is not known.'
            return False
        agent = self.__registry[name]

        if not isinstance(agent, Agent):
            self.__lock.release()
            print 'Agent',name, 'not suspended because it is not local.'
            return False
        if agent.state != AgentState.ACTIVE:
            self.__lock.release()
            print 'Agent ', name, 'not suspended because it is not active.'
            return False

        # Suspend
        try:
            agent.state = AgentState.SUSPENDED
            if in_mem:
                self.__suspended_to_mem[agent.shortname] = agent
            else:
                f=open(AMS.AGENT_STORAGE + agent.shortname, 'w')
                pickle.dump(agent,f)
                f.close()
                
            self.__suspended_shortnames.append(agent.shortname)
            self.__registry[name] = agent.aid
            del self.__runnable_agents[name]
            self.__lock.release()
            print 'Agent',name,'is suspended.'
            return True
        except:
            self.__lock.release()
            print 'Error while suspending',name,'. Agent could be lost.'
            return True
        
    def suspend_agent_until(self, name, until, in_mem=False):
        if self.suspend_agent(name,in_mem):
            shortname = self.__registry.get(name).shortname
            self.__wakeup_lock.acquire()
            try:
                self.__wakeup_dict_times[until].append(shortname)
                self.__wakeup_dict_agents[shortname] = until
                if until not in self.__wakeup_times:
                    self.__wakeup_times.append(until)
                    self.__wakeup_times.sort()
            except:
                self.__wakeup_dict_times[until] = [shortname]
                self.__wakeup_dict_agents[shortname] = until
                self.__wakeup_times.append(until)
                self.__wakeup_times.sort()
                
            self.__wakeup_lock.release()
            self.__save_wakeup_list()
 
    def __save_wakeup_list(self):
        self.__wakeup_lock.acquire()
        f=open('wakeup_list', 'w')
        pickle.dump(self.__wakeup_times,f)
        pickle.dump(self.__wakeup_dict_times,f)
        pickle.dump(self.__wakeup_dict_agents,f)
        f.close()
        self.__wakeup_lock.release()
        
    def __load_wakeup_list(self):
        self.__wakeup_lock.acquire()
        if os.path.exists('wakeup_list'):
            f=open('wakeup_list', 'r')
            self.__wakeup_times = pickle.load(f)
            self.__wakeup_dict_times = pickle.load(f)
            self.__wakeup_dict_agents = pickle.load(f)
            f.close()
        self.__wakeup_lock.release()
                
    # FIXME: Fix locking
    def wakeup_check(self):
        """(Called by behaviour.)"""
        self.__wakeup_lock.acquire()
        if len(self.__wakeup_times) <= 0:
            self.__wakeup_lock.release()
            return
        waked = False
        wakeup_time = self.__wakeup_times[0]
        self.__wakeup_lock.release()
        while datetime.now() >= wakeup_time and self.__waking:
            waked = True
            self.__wakeup_lock.acquire()
            wake_list = self.__wakeup_dict_times.pop(wakeup_time)
            self.__wakeup_lock.release()
            for shortname in wake_list:
                print 'waking:', shortname
                self.__wakeup_lock.acquire()
                self.__wakeup_dict_agents.pop(shortname)
                self.__wakeup_lock.release()
                self.resume_agent(shortname)
            
            self.__wakeup_lock.acquire()
            self.__wakeup_times.remove(wakeup_time)
            if len(self.__wakeup_times) <= 0:
                self.__wakeup_lock.release()
                break
            wakeup_time = self.__wakeup_times[0]
            self.__wakeup_lock.release()
        if waked:
            self.__save_wakeup_list()
        
    def move_agent(self, name, target):
        self.__lock.acquire()
        if name not in self.__registry:
            self.__lock.release()
            print 'Agent', name, 'not moved because it is unknown.'
            return False
        agent = self.__registry[name]
        if not isinstance(agent, Agent):
            self.__lock.release()
            print 'Agent', name, 'not moved because it is not local.'
            return False
        if agent.state != AgentState.ACTIVE:
            self.__lock.release()
            print 'Agent ', name, 'not moved because it is not active.'
            return False
        # Move it
        agent.state = AgentState.TRANSIT
        # Remove all behaviours, in case behaviours are not picklable
        agent.clear_behaviours()
        self.__lock.release()
        self.unregister_agent(agent)
        
        self.__remote_amses_lock.acquire()
        if isinstance(target, Pyro4.core.Proxy):
            target.receive_agent(agent)
        else:
            Pyro4.core.getProxyForURI(target).receive_agent(agent)
        
        print 'Agent', name, 'has been moved.'
        self.__remote_amses_lock.release()
        return True
    
    def get_containers_info(self):
        info = []
        info.append(self.container_info)
        self.__remote_amses_lock.acquire()
        for ams in self.__remote_amses:
            info.append(ams.get_container_info())
        self.__remote_amses_lock.release()
        return info
        
    def get_container_info(self):
        running = self.__get_runnable_count()
        suspended = self.__get_suspended_count()
        return (self.mts.pyrouri,running+suspended,running)

    container_info = property(get_container_info, None, None, "container info")

    def __get_runnable_count(self):
        self.__lock.acquire()
        l = len(self.__runnable_agents)
        self.__lock.release()
        return l

    def __get_suspended_count(self):
        self.__lock.acquire()
        l = len(self.__suspended_shortnames)
        self.__lock.release()
        return l
    
    def get_load(self):
        self.__lock.acquire()
        l = len(self.__suspended_shortnames) + len(self.__runnable_agents)
        self.__lock.release()
        return l

    load = property(get_load, None, None, "load")
    
# Used in IBAS
    def get_move_target(self):
        """Return the location of a possible target to move an agent to"""
        if not len(self.__remote_amses) > 0:
            return None
        
        self.__remote_amses_lock.acquire()
        ams = self.__remote_amses.pop()
        self.__remote_amses.add(ams)
        
        sl = self.load
        rl = ams.get_load()
        target=None
        if sl > rl:
            prob = 1-( float(rl)/float(sl) )
            if random.randint(1,100) < int(prob*100):
                target=ams
        self.__remote_amses_lock.release()
        return target
    
    def receive_agent(self, agent):
        self.__lock.acquire()
        agent.mts = self.mts
        agent.aid.addresses = [self.mts.pyrouri]
        self.__lock.release()
        agent.execute()
        self.register_agent(agent)
        self.invoke_agent(agent.name)
        return True

    def create_agent(self, class_=None, name=None, **namedargs):
        """Create an agent of class class_ with name name and pass
           additional named arguments namedargs to an overridable
           setup() function; don't start the agent yet.
           Return the name of the agent.
        """
        if class_ is None:
            class_ = Agent
        if name is None:
            name = "Agent_%d" % random.randint(0, 1000000)  # FIXME: Assign unused name
        
        if self.exists_agent(name) and name != 'DF':
            print 'Agent with name:',name,'already exists'
            return
        
        agent = class_(AID(shortname=name, hap=self.__hap), self.mts, **namedargs)
        if self.mts.pyrouri:
            agent.aid.add_address(self.mts.pyrouri)
        print 'Agent', agent.name, 'created.'
        self.register_agent(agent)
        agent.state = AgentState.INITIATED
        return agent.name

    def invoke_agent(self, name):
        """Invoke agent of name name
           if it has only been created and not invoked yet
        """
        pass
    
    def __invoke_agent_basic(self, name):
        self.__lock.acquire()
        if name not in self.__registry:
            self.__lock.release()
            print 'Agent', name, 'not invoked because it is unknown.'
            return None
        agent = self.__registry[name]
        if isinstance(agent, AID):
            self.__lock.release()
            print 'Agent', name, 'not invoked because it is not local.'
            return None
        state = agent.state
        if state == AgentState.INITIATED or state == AgentState.SUSPENDED or state == AgentState.TRANSIT:
            agent.state = AgentState.ACTIVE
            self.__runnable_agents[name] = agent
            self.__lock.release()
            return agent
        if state == AgentState.ACTIVE:
            self.__lock.release()
            print 'Agent', name, 'not invoked because already active.'
            return None
        self.__lock.release()
        print 'Agent', name, 'not in a fit state to be invoked.'
        return None
        
    def __invoke_agent_thread(self, name):
        agent = self.__invoke_agent_basic(name)
        if agent is not None:
            threading.Thread(target = agent.run, args=()).start()
            print 'Agent', name, 'invoked.'
    
    def __invoke_agent_nothread(self, name):
        agent = self.__invoke_agent_basic(name)
        if agent is not None and not self.__running:
            self.__running = True
            threading.Thread(target = self.__run_agents, args=()).start()
            print 'Agent', name, 'invoked.'
            
    def __invoke_agent_pool(self, name):
        agent = self.__invoke_agent_basic(name)
        if agent is not None:
            if self.pool == None:
                self.pool = ThreadPool(self.poolsize)
            self.pool.reschedule(agent)
            print 'Agent', name, 'invoked.'
 
    def __run_agents(self):
        """Execute the (non-threaded) agents"""
        while len(self.__runnable_agents) > 0:
            for agent in self.__runnable_agents.values():                
                if agent.state == AgentState.ACTIVE:
                    agent.run_once()
            time.sleep(0.001)
        self.__running = False

    def invoke_all_agents(self):
        self.__lock.acquire()
        names = self.__registry.keys()
        self.__lock.release()
        for name in names:
            self.invoke_agent(name)

    def start_agent(self, *formalargs, **namedargs):
        """Create and invoke an agent.

           Takes exactly the same arguments as create_agent() but
           does not return anything.
        """
        name = self.create_agent(*formalargs, **namedargs)
        if name is not None:
            self.invoke_agent(name)
        
    def exists_agent(self, name, localonly=False):
        self.__lock.acquire()
        if name in self.__registry:
            self.__lock.release()
            return True
        self.__lock.release()
        if localonly:
            return False
        self.__remote_amses_lock.acquire()
        for ams in self.__remote_amses:
            if ams.exists_agent(name, localonly=True):
                self.__remote_amses_lock.release()
                return True
        if self.__ams_server is not None:
            if self.__ams_server.exists_agent(name, localonly=True):
                self.__remote_amses_lock.release()
                return True
        self.__remote_amses_lock.release()
        return False
 
    #
    # Registration methods
    #

    def __register_agent_local(self, agent):
        """Register the agent here.
           The agent parameter can be either an agent or an AID object.
           Return True if agent is hereby registered; False if not.
        """
        self.__lock.acquire()
        name = agent.name
        if name in self.__registry:
            print 'Not registering agent', name + ': an agent by that name was already registered.'
            self.__lock.release()
            return False
        self.__registry[name] = agent
        print 'Agent', name, 'has been registered.'
        self.__lock.release()
        return True

    def register_agent(self, agent, localonly=None):
        """Register the given agent at this platform
           and also at others unless local is set to True.
           Agent can be an agent or AID object.
           Return nothing.
           Overridden.
        """
        pass

    def __register_agent_basic(self, agent, localonly=None):
        self.__register_agent_local(agent)
    
    def __register_agent_retrieve(self, agent, localonly=None):
        if not self.exists_agent(agent.name) or agent.shortname == 'DF':
            self.__register_agent_local(agent)
    
    def __register_agent_update(self, agent, localonly=False):
        if localonly or agent.shortname == 'DF':
            self.__register_agent_local(agent)
            return
        # Not localonly and not the DF
        if not self.exists_agent(agent.name):
            self.__register_agent_local(agent)
            self.__remote_amses_lock.acquire()
            for ams in self.__remote_amses:
                ams.register_agent(agent.aid, localonly=True)
            self.__remote_amses_lock.release()
                
    def __register_agent_client(self, agent, localonly=False):
        if agent.shortname == 'DF' or not self.__ams_server.exists_agent(agent.name):
            if self.__register_agent_local(agent) and agent.shortname != 'DF' and not localonly:
                self.__ams_server.register_agent(agent.aid)
    
    def __unregister_agent_local(self, agent):
        """Unregister the agent here.
           The agent parameter can be either an agent or an AID object.
           Return True if the agent is hereby unregistered; False if not.
        """
        name = agent.name
        self.__lock.acquire()
        if name in self.__runnable_agents:
            del self.__runnable_agents[name]
        if name in self.__registry:
            del self.__registry[name]
            self.__lock.release()
            print 'Agent', name, 'has been unregistered.'
            return True
        else:
            self.__lock.release()
            print 'Not unregistering agent', name + ': it is not registered.'
            return False

    def unregister_agent(self, agent, localonly=None):
        """Unregister the given agent from the platform
           and also at others unless localonly is set to True.
           Agent can be an agent or AID object.
           Return nothing.
           Overridden.
        """
        pass
    
    def __unregister_agent_basic(self, agent, localonly=None):
        self.__unregister_agent_local(agent)

    def __unregister_agent_retrieve(self, agent, localonly=False):
        if not self.__unregister_agent_local(agent) and not localonly:
            self.__remote_amses_lock.acquire()
            for ams in self.__remote_amses:
                if ams.unregister_agent(agent, localonly=True):
                    break
            self.__remote_amses_lock.release()
    
    def __unregister_agent_update(self, agent, localonly=False):
        if self.__unregister_agent_local(agent) and agent.shortname != 'AMS' and agent.shortname != 'DF' and not localonly:
            self.__remote_amses_lock.acquire()
            for ams in self.__remote_amses:
                ams.unregister_agent(agent.aid, localonly=True)
            self.__remote_amses_lock.release()
    
    def __unregister_agent_client(self, agent, localonly=None):
        self.__unregister_agent_local(agent)
        if agent.shortname != 'DF' and agent.shortname != 'AMS':
            self.__ams_server.unregister_agent(agent.aid)

    #
    # Messaging methods
    #

    def send(self, aid, msg):
        """Send an ACL message to recipients"""
        # Check whether on same platform;
        # if not, send via pyro or http
        msg.sender = aid
        for rec in msg.receivers:
            print "****************************", rec
            recname = rec.name
            if recname == self.name:
                a = self
            else:
                if recname in self.__registry:
                    a = self.__registry[recname]
                else:
                    print recname, 'not found'
                    return

            a.receive_message(copy.deepcopy(msg.encode_ACL()))

            # Python-Docs-2.3.4/lib/module-copy.html
            # should take a look at pickling: Python-Docs-2.3.4/lib/module-pickle.html

            # log message -> Logger
            '''
            # Python 2.3 Logging:
            logger = logging.getLogger('spyse')
            handler = logging.FileHandler('spyse.log')
            # handler2 = logging.StreamHandler(???) -> stdout ?
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            logger.info('sending a message')
            '''
            #logging.error('sending a message')

    def die(self):
        print "Killing all agents on the platform."
        self.__waking=False
        df_ref=None
        for a in self.__registry.values():
            if isinstance(a, Agent) and a.shortname != 'AMS':
                if a.shortname != 'DF':
                    a.die()
                else:
                    print 'Kill DF as the second last agent...'
                    df_ref = a
                    
        if df_ref is not None:
            time.sleep(1)
            print 'Killing the DF.'
            df_ref.die()
        
        self.__remote_amses_lock.acquire()
        for ams in self.__remote_amses:
            ams.remove_other(self.getProxy())
        self.__remote_amses_lock.release()
      
        print 'Writing suspended agents to hard disk.'
        for agent in self.__suspended_to_mem.values():
            f = open(AMS.AGENT_STORAGE + agent.shortname, 'w')
            pickle.dump(agent, f)
            f.close()
        
        Agent.die(self)
        if self.pool is not None:
            self.pool.die()

    def get_agent(self, shortname):
        """ returns an agent object, or it's AID, with the given shortname 
            or None if it's not locally available 
        """
        if shortname in self.__suspended_shortnames:
            print 'Resuming suspended agent possibly before wakeup time',shortname
            return self.__resume_agent(shortname)
            
        name = shortname + "@" + self.__hap.name
        return self.__registry.get(name)

    def find_agent(self, shortname, localonly=None):
        """ returns the AID of the agent with the given name. """
        pass        
        
    def __find_agent_basic(self, shortname, localonly=None):
        agent = self.get_agent(shortname)
        if isinstance(agent, AID):
            return agent
        elif isinstance(agent, Agent):
            return agent.aid
        else:
            return None
        
    def __find_agent_retrieve(self, shortname, localonly=False):
        agent = self.get_agent(shortname)
        if isinstance(agent, Agent):
            return agent.aid
        if isinstance(agent, AID):
            return agent
        if localonly:
            return None
        self.__remote_amses_lock.acquire()
        for ams in self.__remote_amses:
            aid = ams.find_agent(shortname, localonly=True)
            if aid:
                self.__remote_amses_lock.release()
                return aid
        self.__remote_amses_lock.release()
        return None
    
    def __find_agent_client(self, shortname, localonly=None):
        agent = self.get_agent(shortname)
        if agent:
            return agent.aid
        return self.__ams_server.find_agent(shortname)
    
    def find_agents(self):
        """Return a list of AIDS for all agents this AMS knows about"""
        agents = []
        self.__lock.acquire()
        regvals = self.__registry.values()
        self.__lock.release()
        # FIXME: Check thread safety
        for a in regvals:
            if isinstance(a, AID):
                agents.append(a)
            else:
                agents.append(a.aid)
        return agents

