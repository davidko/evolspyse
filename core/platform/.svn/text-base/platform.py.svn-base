"""Spyse platform module"""
__version__ = "0.2"

import os
import socket
from datetime import datetime

from spyse.core.agents.aid import AID
from spyse.core.platform.constants import Dist, NsMode
from spyse.core.platform.hap import HAP
from spyse.core.platform.ams import AMS
from spyse.core.platform.df import DF
from spyse.core.mts.mts import MTS
import spyse.core.semant.environment

from threading import Thread
import thread
import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError
from Pyro.errors import NamingError as PyroNamingError


#
# Platform is a singleton, although currently the class does not
# enforce this.  State is stored in the class object.
#
# We were going to turn it into a borg, but we will wait and merge
# Platform and App into a new borg called 'Container'.
#

class Platform(object):

    ams = None
    mts = None
    running = None    # Used to stop the Pyro daemon
    
    def __init__(self, port, threadmeth, poolsize, dist, env, nsmode, ns_host=None):
        assert port == int(port)
        assert poolsize == int(poolsize)
        cls = self.__class__
        myname = self.__get_domain_name() + ':' + str(port)
        myhap = HAP(myname)

        w = 72
        print datetime.now()
        print "="*w
        print "==" + ("Spyse platform, version " + __version__).center(w-4) + "=="
        print "==" + ("http://spyse.sf.net, LGPL").center(w-4) + "=="
        print "==" + ("Starting at " + myname).center(w-4) + "=="
        print "="*w
        print
        
        # Pyro parameters
        pyrogroup = ':spyse'         
        pyroloc = myname.replace(".","+")
        Pyro.config.PYRO_PORT = port
        Pyro.config.PYRO_MOBILE_CODE = 1
        Pyro.core.initServer()    
        # Create Pyro daemon
        cls.daemon = Pyro.core.Daemon()
        cls.running = True
        cls.nameserver = None
        cls.nslock = thread.allocate_lock()
        spyse.core.semant.environment.dist = env
        spyse.core.semant.environment.daemon = cls.daemon
        spyse.core.semant.environment.pyroloc = pyroloc
        
        if nsmode == NsMode.NONE:
            print 'Will not use a nameserver.'
            cls.nameserver = None
        elif nsmode == NsMode.LOCAL:
            print 'Will use a local nameserver.'
            Pyro.config.PYRO_NS_HOSTNAME = 'localhost'
            try:
                nslocator = Pyro.naming.NameServerLocator()
                cls.nameserver = nslocator.getNS()
            except Pyro.errors.PyroError:
                print "No nameserver could be found locally. Exiting."
                return
            else:
                print 'Nameserver found locally.'
        elif nsmode == NsMode.REMOTE:
            # Remote Pyro mode
            if ns_host is None:
                print 'Trying to find a remote nameserver.'
                Pyro.config.PYRO_NS_HOSTNAME = ''
            else:
                print 'Trying to find a nameserver at', ns_host + '.'
                Pyro.config.PYRO_NS_HOSTNAME = ns_host
            try:
                nslocator = Pyro.naming.NameServerLocator()
                cls.nameserver = nslocator.getNS()
            except Pyro.errors.PyroError:
                print "No nameserver could be found. Exiting."
                return
            else:
                print 'Nameserver found.'
        else:
            raise ValueError("Unrecognized nsmode")

        spyse.core.semant.environment.nameserver = cls.nameserver

        if nsmode == NsMode.NONE:
            dist = Dist.NONE
            env = 'normal'
        else:
            cls.daemon.useNameServer(cls.nameserver)
            try:
                cls.nameserver.createGroup(pyrogroup)
            except PyroNamingError:
                # Happens if the name already exists
                pass        
            Pyro.config.PYRO_NS_DEFAULTGROUP = pyrogroup
            try:
                remote_hap = Pyro.core.getAttrProxyForURI("PYRONAME://HAP")
            except:
                # Happens if the 'HAP' not yet registered
                # FIXME: There appears to be a race here
                hap_delegate = Pyro.core.ObjBase()
                hap_delegate.delegateTo(myhap)
                cls.daemon.connect(hap_delegate,'HAP')
            else:
                myhap = HAP(remote_hap.name)

        cls.mts = MTS(hap=myhap)
        mts_pyrouri = cls.daemon.connect(cls.mts, pyroloc+'/mts')
        cls.mts.pyrouri = mts_pyrouri
        print "-- Platform", myname, "has created the Message Transport System"

        cls.ams = AMS(cls.nameserver, myhap, cls.mts, threadmeth, poolsize)
        uri = cls.daemon.connect(cls.ams, pyroloc+'/ams')
        cls.ams.aid.add_address(mts_pyrouri)
        cls.ams.init_dist(dist)
        print "-- Platform", myname, "has started the Agent Management System agent"
        cls.mts.ams = cls.ams       
        print "-- Platform", myname, "has registered the AMS with the MTS"

        cls.ams.start_agent(DF, name='DF', nameserver=cls.nameserver)
        cls.daemon.connect(cls.ams.get_agent('DF'), pyroloc+'/df')
        cls.ams.get_agent('DF').init_dist(dist)
        print "-- Platform", myname, "has started the Directory Facilitator agent"

        Thread(target = cls.daemon.requestLoop, kwargs={'condition': self.is_running}).start()

    def __get_host_name(self):
        return socket.gethostname()

    def __get_domain_name(self):
        return socket.getfqdn(self.__get_host_name())

    def __get_population(self):
        return self.__class__.ams.population

    # Used for testing
    population = property(__get_population, None, None, "population")

    @classmethod
    def is_running(cls):
        return cls.running

    running = property(is_running, None, None, "running")

    @classmethod
    def shutdown(cls):
        """Shut down the platform"""
        cls.ams.die()
        cls.daemon.shutdown()
        cls.running = False
        del cls.ams
        del cls.mts

    def create_agent(self, *formalargs, **namedargs):
        """Takes exactly the same arguments as the AMS method of the same name"""
        return self.__class__.ams.create_agent(*formalargs, **namedargs)

    def invoke_all_agents(self):
        self.__class__.ams.invoke_all_agents()

    def start_agent(self, *formalargs, **namedargs):
        """Takes exactly the same arguments as the AMS method of the same name"""
        # Create and invoke
        self.__class__.ams.start_agent(*formalargs, **namedargs)

