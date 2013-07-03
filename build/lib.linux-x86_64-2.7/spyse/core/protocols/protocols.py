"""Spyse basic protocols module"""

import time
from datetime import datetime
from random import randint
from spyse.core.behaviours.behaviours import Behaviour
from spyse.core.behaviours.fsm import FSMBehaviour
from spyse.core.content.content import ACLMessage


class Protocol(object):

    # FIPA interaction protocols
    FIPA_REQUEST = "fipa-request"
    FIPA_QUERY =  "fipa-query"
    FIPA_REQUEST_WHEN = "fipa-request-when"
    FIPA_BROKERING = "fipa-brokering"
    FIPA_RECRUITING = "fipa-recruiting"
    FIPA_PROPOSE = "fipa-propose"
    FIPA_SUBSCRIBE = "fipa-subscribe"
    FIPA_ENGLISH_AUCTION = "fipa-auction-english"
    FIPA_DUTCH_AUCTION = "fipa-auction-dutch"
    FIPA_CONTRACT_NET = "fipa-contract-net"  
    FIPA_ITERATED_CONTRACT_NET = "fipa-iterated-contract-net"


class Participant(FSMBehaviour):
    pass


class AchieveREParticipant(Participant):
    pass


# FIPA Propose Interaction Protocol
# http://www.fipa.org/specs/???


class ProposeParticipant(Participant):
    pass

