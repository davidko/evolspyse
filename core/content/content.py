"""Spyse content module"""

from spyse.core.agents.aid import AID
import time
import copy
from random import randint

# ACL = Agent Communication Language

class MessageTemplate(object):
    # FIPA ACL message slots (FIPA ACL Message Structure Specification, SC00061G):
    # http://www.fipa.org/specs/fipa00061/SC00061G.html
    #
    # PERFORMATIVE = "performative"        # Type of communicative acts
    # SENDER = "sender"                    # Participant in communication
    # RECEIVER = "receiver"                # Participant in communication
    # REPLY_TO = "reply-to"                # Participant in communication
    # CONTENT = "content"                  # Content of message
    # LANGUAGE = "language"                # Description of content
    # ENCODING = "encoding"                # Description of content
    # ONTOLOGY = "ontology"                # Description of content
    # PROTOCOL = "protocol"                # Control of conversation
    # CONVERSATION_ID = "conversation-id"  # Control of conversation
    # REPLY_WITH = "reply-with"            # Control of conversation
    # IN_REPLY_TO = "in-reply-to"          # Control of conversation
    # REPLY_BY = "reply-by"                # Control of conversation

    # constants identifying the FIPA performatives
    # http://www.fipa.org/specs/fipa00037/SC00037J.html
    ACCEPT_PROPOSAL = "accept-proposal"
    AGREE = "agree"
    CANCEL = "cancel"
    CFP = "cfp"
    CONFIRM = "confirm"
    DISCONFIRM = "disconfirm"
    FAILURE = "failure"
    INFORM = "inform"
    INFORM_IF = "inform-if"
    INFORM_REF = "inform-ref"
    INFORM_DONE = "INFORM_DONE"     # Not listed
    NOT_UNDERSTOOD = "not-understood"
    PROPAGATE = "propagate"
    PROPOSE = "propose"
    PROXY = "proxy"
    QUERY_IF = "query-if"
    QUERY_REF = "query-ref"
    REFUSE = "refuse"
    REJECT_PROPOSAL = "reject-proposal"
    REQUEST = "request"
    REQUEST_WHEN = "request-when"
    REQUEST_WHENEVER = "request-whenever"
    SUBSCRIBE = "subscribe"
    UNKNOWN = "unknown"

    # Allowed attribute names
    # With underscores, not hyphens
    __slots__ = ( "sender", "receivers", "performative", "protocol", "encoding", "language", "ontology", "content", "reply_to", "reply_with", "in_reply_to", "reply_by", "conversation_id" )

    def __init__(self, performative=None):
        self.performative = performative

    def __get_dict(self):
        d = {}
        for s in self.__slots__:
            a = getattr(self, s, None)
            if a is not None:
                d[s] = a
        return d

    dict = property(__get_dict, None, None, "dictionary of attributes")

class ACLMessage(MessageTemplate):
    def __init__(self, performative=None):
        # Set mandatory attributes
        self.sender = None
        self.receivers = set()
        MessageTemplate.__init__(self, performative);

    def set_conversation_id(self):
        """Set a conversation ID"""
        self.conversation_id = 'cid' + str(hash(self)) + str(time.time()) + str(randint(0,1000000))

    def create_reply(self, performative=MessageTemplate.AGREE):
        reply = copy.copy(self)
        reply.performative = performative
        reply.receivers = set([reply.sender])
        reply.content = None
        reply.sender = None
        return reply

    # Syntactic representation of ACL in string form 
    # <a href=http://www.fipa.org/specs/fipa00070/XC00070f.html>FIPA Spec</a>

    # Syntactic representation of ACL in XML form
    # <a href=http://www.fipa.org/specs/fipa00071/XC00071b.html>FIPA Spec</a>

    # Syntactic representation of ACL in bit-efficient form
    # <a href=http://www.fipa.org/specs/fipa00069/XC00069e.html>FIPA Spec</a>
    def encode_ACL(self): # FIPA ACL structure
        return self

    def decode_ACL(self): # FIPA ACL structure
        return self


class TemplateSet(set):
    pass
