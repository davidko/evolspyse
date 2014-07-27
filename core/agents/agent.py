"""Spyse agent with basic functionality module"""

# TODO: try dummy_threading as option
#try:
#    import threading as _threading
#except ImportError:
#    import dummy_threading as _threading

import threading
import thread
import Queue
import time
import copy
from collections import deque
from datetime import datetime

from spyse.core.agents.aid import AID
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.content.content import TemplateSet, MessageTemplate
from spyse.core.platform.constants import AgentState

#class Agent(threading.Thread):
class Agent(object):
    """Basic Spyse agent"""

    def __init__(self, name, mts, **namedargs):
        # Normally this should not normally be overridden
        # Override setup() instead
        self.mts = mts
        if isinstance(name, AID):
            self.__aid = name
        else:
            self.__aid = AID(name)
        self.state = None  # Manipulated by AMS
        self.__behaviours = []
        self.__queue = TemplateQueue()
        self.setup(**namedargs)
    
    def __getstate__(self):
        # Called when the (suspended) agent is stored to disk
        # MTS is not saved and should be restored on loading
        # Template queue is converted to a dict in order to save it
        d = copy.copy(self.__dict__)
        del d['mts']
        tq = d['_Agent__queue']
        ntq = tq._TemplateQueue__queue
        d['_Agent__queue'] = ntq
        return d
    
    def __setstate__(self, d):
        # Called when (suspended) agent is loaded from disk
        tq = d['_Agent__queue']
        rtq = TemplateQueue()
        rtq._TemplateQueue__queue = tq
        d['_Agent__queue'] = rtq
        self.__dict__ = d

    def __get_name(self):
        return self.__aid.name

    def __set_name(self, name):
        self.__aid.name = name
        super(Agent, self).setName(name)
        
    def __get_shortname(self):
        return self.__aid.shortname
    
    def __get_aid(self):
        return self.__aid

    name = property(__get_name, __set_name, None, "name of this agent")
    shortname = property(__get_shortname, None, None, "shortname of this agent")
    aid = property(__get_aid, None, None, "aid of this agent")

    def setup(self):
        # Override in subclass for initialisation
        print 'Default setup function of', self.__get_name()
        self.add_behaviour(Behaviour())

    def run(self):
        """Run through all behaviours, executing the action() of each"""
        while self.state == AgentState.ACTIVE:
            if self.__behaviours and len(self.__behaviours) > 0:
                for b in self.__behaviours:
                    #print self.shortname,'executing',b.name
#TODO: should pausing be introduced globally or should behaviours decide themselves?
#                    if not b.paused():
#                        b.action()
                    b.action()
                    if b.done():
                        b.take_down()
                        self.remove_behaviour(b)
            else:
                try:
                    if self.mts.ams is not None:
                        self.mts.ams.unregister_agent(self)
                except:
                    print 'error at unregistering',self.name
                #print 'Agent', self.name, 'has died.' 
                break
            time.sleep(0.001) # Keep us from using all CPU
            #time.sleep(0)
        #print self.name,'stopped execution'
    
    def run_once(self):
        """Pick the first behaviour from the list and execute it."""
        if self.__behaviours and len(self.__behaviours) > 0:
            b = self.__behaviours[0]
            b.action()
            if b.done():
                b.take_down()
                self.remove_behaviour(b)
                if len(self.__behaviours) == 0:
                    self.mts.ams.unregister_agent(self)
                    return 1
            else:
                self.__behaviours.remove(b)
                self.__behaviours.append(b)
        else:
            self.mts.ams.unregister_agent(self)
            return 1 

    def die(self):
        for b in self.__behaviours:
            b.set_done()

    def suspend(self,in_mem=False):
        self.mts.ams.suspend_agent(self.name,in_mem)

    def suspend_until(self, until,in_mem=False):
        self.mts.ams.suspend_agent_until(self.name, until,in_mem)
        
    def resume(self):
        """ will be called on resume, override with user code"""
        pass
        
    def move(self, host):
        self.mts.ams.move_agent(self.name, host)

    def get_message(self, template=None):
        try:
            msg = self.__queue.get(template)
            if msg is None:
                return None
            else:
                return msg.decode_ACL()
        except Queue.Empty:
            return None

    def receive_message(self, msg):
        #self.__receive_messageLock = threading.Condition(threading.Lock())
        #self.__receive_messageLock.acquire()
        #print 'Agent', self.name, 'receives message.'
        if msg is not None:
            self.__queue.put(msg)
            #print 'Agent', self.name, 'received message', msg
            #print 'Agent', self.name, self.__queue.qsize(), 'messages in queue'
        #self.__receive_messageLock.release()

    def send_message(self, msg):
        return self.mts.send(self.__aid, msg)

        # Messages are sent via the MTS in order to provide for agents'
        # autonomy and privacy and in order to abstract from transport layer.
        # However, this may be a bottleneck when lots of mesages are sent.
        # We should to look into p2p approaches.

    def add_behaviour(self, behaviour, name=None):
        assert isinstance(behaviour, Behaviour), "Trying to add an object that is not a Behaviour"
        behaviour.agent = self
        if name is not None:
            behaviour.name = self.name + '.' + name
        self.__behaviours.append(behaviour)

    def remove_behaviour(self, behaviour):
        try:
            self.__behaviours.remove(behaviour)
        except: pass

    def clear_behaviours(self):
        self.__behaviours = []
        
    def num_behaviours(self):
        return len(self.__behaviours)

    def _set_hap(self, hap):
        """ This function should only be used by the agency to reset the agent's
            HAP after the agent has migrated. """
        self.__aid.hap = hap

class TemplateQueue(object):
    def __init__(self):
        self.__queue = deque()
        self.__lock = thread.allocate_lock()
    
    def put(self, msg):
        self.__lock.acquire()
        self.__queue.append(msg)
        self.__lock.release()
    
    """TemplateQueue for Agent"""
    def get(self, template=None):
        self.__lock.acquire()
        res=None
        if template is None:
            if len(self.__queue) > 0:
                res = self.__queue.popleft()
        else:
            # Search from the head to the tail of the queue,
            # and return the first match
            for i in range(len(self.__queue)):
                msg = self.__queue.popleft()
                if self._compare(msg, template):
                    res = msg
                    break
                else:
                    self.__queue.append(msg)
        self.__lock.release()
        return res

    def _compare(self, msg, template):
        if isinstance(template,MessageTemplate):
            template = template.dict
        for attr, tmp_val in template.iteritems():
            attr = attr.replace('-','_') # convert FIPA string to Python names
            msg_val = getattr(msg, attr, None)
            # Allow multiple values in template
            if type(tmp_val) is not TemplateSet:
                tmp_val = TemplateSet([tmp_val])
            if msg_val not in tmp_val:
                return False
        return True


class Logger(Agent):
    """Logging agent, writes output to console or file"""

    def startup(self, args):
        self.__log = []
        # subscribe to updates of all agents
        # subscribe to creation of new agents and their updates

    def get_log(self):
        return self.__log

    def add_log(self, log):
        self.__registry[agent.name] = agent

