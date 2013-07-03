"""Spyse app module"""

import os
import sys
import getopt
import time
from threading import Thread

import Pyro4.naming
import Pyro4.nsc

from spyse.core.platform.constants import Dist, NsMode, ThreadMeth
from spyse.core.platform.platform import Platform


class App(object):

    DEFAULT_PORT = 9000
    DEFAULT_POOLSIZE = 100

    def __init__(self,
            port=DEFAULT_PORT,
            distribution=None,
            env='normal',
            ns=None,
            poolsize=DEFAULT_POOLSIZE,
            threading=None
        ):
        #
        # Process options and arguments
        #
        opts = None
        args = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hp:", 
                ["distribution=", "env=", "help", "poolsize=", "port=", "ns=", "threading="]
            )
        except getopt.error, msg:
            print msg
            print "for help use --help"
            return 2
        if not opts is None:
            for o, a in opts:
                if o in ("-h", "--help"):
                    print __doc__
                    return 0
                elif o in ("--distribution", "--dist"):
                    distribution = a
                elif o in ("--env"):
                    env = a
                elif o in ("--poolsize"):
                    poolsize = int(a)
                elif o in ("-p", "--port"):
                    port = int(a)
                elif o in ("--ns"):
                    ns = a
                elif o in ("--threading"):
                    threading = a
                else:
                    print "Unrecognized option", o

        if distribution == 'broadcast-update' or distribution == 'bcast_update':
            dist = Dist.BCAST_UPDATE
        elif distribution == 'broadcast-retrieve' or distribution == 'bcast_retrieve':
            dist = Dist.BCAST_RETRIEVE
        elif distribution == 'server':
            dist = Dist.CENTRAL_SERVER
        elif distribution == 'client':
            dist = Dist.CENTRAL_CLIENT
        else:
            dist = Dist.NONE

        ns_host = None
        if ns == 'start':
            start_ns = True
            nsmode = NsMode.LOCAL
        else:
            start_ns = False
            if ns == 'local':
                nsmode = NsMode.LOCAL
            elif ns == 'remote':
                nsmode = NsMode.REMOTE
                ns_host = None
            elif ns == str(ns):
                nsmode = NsMode.REMOTE
                ns_host = ns
            else:
                nsmode = NsMode.NONE

        if threading == 'off':
            threadmeth = ThreadMeth.OFF
        elif threading == 'pool':
            threadmeth = ThreadMeth.POOL
        else:
            threadmeth = ThreadMeth.NORMAL

        if start_ns:
            print 'Starting a Pyro nameserver'
            self.__nsstarter = Pyro4.naming.NameServerStarter()
            Thread(target = self.__nsstarter.start, kwargs={'allowmultiple': 1}).start()
            self.__nsstarter.waitUntilStarted(timeout=10)
            
        #
        # Go
        #
        self.__platform = Platform(port, threadmeth, poolsize, dist, env, nsmode, ns_host)
        print
        print "Press control-C to shut down this Spyse platform."
        print

        # Call the overridden run method
        self.run(args)

        try:
            # FIXME: It would be better either to sleep indefinitely
            # or to poll the platform for number of agents reaching zero
            while Platform.running:
                time.sleep(60)
        except KeyboardInterrupt:
            print "Keyboard interrupt signal received."
            self.__platform.shutdown()
        if start_ns:
            print 'Killing the nameserver'
            #self.__nsstarter.shutdown()   ### Does not work
            Pyro4.nsc.main("shutdown")
            #os.execlp('pyro-nsc', 'pyro-nsc', 'shutdown')  ### Annoying locator timeout
        print 'Exiting.'
        sys.exit()

    def create_agent(self, *formalargs, **namedargs):
        """Takes exactly the same arguments as the Platform method of the same name"""
        return self.__platform.create_agent(*formalargs, **namedargs)

    def invoke_all_agents(self):
        """Takes exactly the same arguments (i.e., none) as the Platform method of the same name"""
        self.__platform.invoke_all_agents()

    def start_agent(self, *formalargs, **namedargs):
        """Takes exactly the same arguments as the Platform method of the same name"""
        self.__platform.start_agent(*formalargs, **namedargs)

    def run(self, args):
        # Override me
        # args is the list of command line arguments
        pass
