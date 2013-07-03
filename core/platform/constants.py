"""Spyse core platform constants module"""
__version__ = "0.2"


# TODO: Use enums?


class Dist(object):
    # Distribution modes
    # None               : The Spyse platform is not distributed
    # Broadcast Update   : Every AMS instance knows the AID of every agent
    # Broadcast Retrieve : When searching for an agent the AMS will consult other AMSs
    # Central Client     : The AMS will consult a server when he can't find an agent locally
    # Central Server     : This AMS will act as a central server for agent registration
    NONE = 'NONE'
    BCAST_UPDATE = 'BCAST_UPDATE'
    BCAST_RETRIEVE = 'BCAST_RETRIEVE'
    CENTRAL_CLIENT = 'CENTRAL_CLIENT'
    CENTRAL_SERVER = 'CENTRAL_SERVER'


class NsMode(object):
    NONE = 'NONE'
    LOCAL = 'LOCAL'
    REMOTE = 'REMOTE'


class ThreadMeth(object):
    NORMAL = 'NORMAL'
    OFF = 'OFF'
    POOL = 'POOL'

class AgentState(object):
    # Agent state names as specified by FIPA
    INITIATED = 'INITIATED'
    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'
    WAITING = 'WAITING'
    TRANSIT = 'TRANSIT'

