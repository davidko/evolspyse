"""Spyse codec module"""

import xml.dom.minidom

#from xml.dom.minidom import DOMImplementation
from xml.dom import Node
#from xml.dom.ext import PrettyPrint

from spyse.core.agents.aid import AID
from spyse.core.agents.agent import Agent
from spyse.core.content.content import ACLMessage

class ACLCodec(object):

    FIPA_MESSAGE = "fipa-message"
    ACT = "act"

    def __init__(self):
        pass

    def encode(self, msg):
        pass

    def decode(self, msg):
        pass


class StringCodec(ACLCodec):
    pass


class XMLCodec(ACLCodec):
    def encode_ACL(msg):
        domi = xml.dom.minidom.DOMImplementation()
        dtd = domi.createDocumentType(FIPA_MESSAGE, "FIPA ACL Message Representation in XML", "fipa.acl.rep.xml.std.dtd")
        dom = domi.createDocument(None, FIPA_MESSAGE, dtd)

        fipa_msg = dom.getElementsByTagName(FIPA_MESSAGE).item(0)

        d = msg.performative
        if d is not None:
            __add_performative(dom, fipa_msg, d)

        d = msg.conversation_id
        if d is not None:
            __add_conversation_id(dom, fipa_msg, d)

        d = msg.sender
        if d is not None:
            __add_sender(dom, fipa_msg, d)

        d = msg.receivers
        for di in d:
            __add_receiver(dom, fipa_msg, di)

        d = msg.reply_to
        if d is not None:
            __add_reply_to(dom, fipa_msg, d)

        d = msg.content
        if d is not None:
            __add_content(dom, fipa_msg, d)

        d = msg.language
        if d is not None:
            __add_language(dom, fipa_msg, d)

        d = msg.encoding
        if d is not None:
            __add_encoding(dom, fipa_msg, d)

        d = msg.ontology
        if d is not None:
            __add_ontology(dom, fipa_msg, d)

        d = msg.protocol
        if d is not None:
            __add_protocol(dom, fipa_msg, d)

        d = msg.reply_with
        if d is not None:
            __add_reply_with(dom, fipa_msg, d)

        d = msg.in_reply_to
        if d is not None:
            __add_in_reply_to(dom, fipa_msg, d)

        d = msg.reply_by
        if d is not None:
            __add_reply_by(dom, fipa_msg, d)

        #return dom.toxml("utf-8")
        return dom.toprettyxml()    #TODO: replace by toxml()

    def __add_agent_identifier(dom, node, detail):
        aid = dom.createElement("agent-identifier")

        # name
        name = dom.createElement("name")
        aid.appendChild(name)
        #TODO: check whether id is used ==> refid
        name.setAttribute("id", detail.name)

        # addresses
        __add_addresses(dom, aid, detail.getHAP())

        # resolvers
        #__add_resolvers(dom, node, detail)

        # user-data
        #__add_user_data(dom, node, detail)

        node.appendChild(aid)

    def __add_addresses(dom, node, detail):
        addresses = dom.createElement("addresses")
        url = dom.createElement("url")
        url.setAttribute("href", detail)
        addresses.appendChild(url)
        node.appendChild(addresses)

    def __add_resolvers(dom, node, detail):
        pass

    def __add_user_data(dom, node, detail):
        pass

    def __add_performative(dom, node, detail):
        node.setAttribute(ACT, detail)

    def __add_conversation_id(dom, node, detail):
        node.setAttribute(CONVERSATION_ID, detail)
        conversation_id = dom.createElement(CONVERSATION_ID)
        conversation_id.appendChild(dom.createTextNode(detail))
        node.appendChild(conversation_id)

    def __add_sender(dom, node, detail):
        #sender = Element("sender")
        #sender.nodeType = Node.ELEMENT_NODE
        sender = dom.createElement("sender")
        #fipa_msg.appendChild(sender)
        __add_agent_identifier(dom, sender, detail)
        #sender.appendChild(dom.createTextNode('XML processing with Python'))
        #return sender
        node.appendChild(sender)

    def __add_receiver(dom, node, detail):
        receiver = dom.createElement("receiver")
        for r in detail:
            aid = __add_agent_identifier(dom, receiver, r)
            #receiver.appendChild(aid)
        node.appendChild(receiver)

    def __add_reply_to(dom, node, detail):
        reply_to = dom.createElement(REPLY_TO)
        __add_agent_identifier(dom, reply_to, detail)
        node.appendChild(reply_to)

    def __add_content(dom, node, detail):
        content = dom.createElement(CONTENT)
        content.appendChild(dom.createTextNode(detail))
        node.appendChild(content)

    def __add_language(dom, node, detail):
        language = dom.createElement(LANGUAGE)
        language.appendChild(dom.createTextNode(detail))
        node.appendChild(language)

    def __add_encoding(dom, node, detail):
        encoding = dom.createElement(ENCODING)
        encoding.appendChild(dom.createTextNode(detail))
        node.appendChild(encoding)

    def __add_ontology(dom, node, detail):
        ontology = dom.createElement(ONTOLOGY)
        ontology.appendChild(dom.createTextNode(detail))
        node.appendChild(ontology)

    def __add_protocol(dom, node, detail):
        protocol = dom.createElement(PROTOCOL)
        protocol.appendChild(dom.createTextNode(detail))
        node.appendChild(protocol)

    def __add_reply_with(dom, node, detail):
        reply_with = dom.createElement(REPLY_WITH)
        reply_with.appendChild(dom.createTextNode(detail))
        node.appendChild(reply_with)

    def __add_in_reply_to(dom, node, detail):
        in_reply_to = dom.createElement(IN_REPLY_TO)
        in_reply_to.appendChild(dom.createTextNode(detail))
        node.appendChild(in_reply_to)

    def __add_reply_by(dom, node, detail):
        reply_by = dom.createElement(REPLY_BY)
        reply_by.setAttribute('time', detail)
        node.appendChild(reply_by)

    #==================================================

    def decode_ACL(emsg):
        print "\n*** decoding ***\n"
        msg = ACLMessage()
        dom = xml.dom.minidom.parseString(emsg)
        __handleFipamessage(dom.getElementsByTagName(FIPA_MESSAGE)[0], msg)
        return msg

    def __handleFipamessage(fipamessage, msg):
        performative = fipamessage.getAttribute(ACT)
        if performative is not None:
            msg.performative = performative
        print ACT, performative

        sender = fipamessage.getElementsByTagName(SENDER)[0]
        if sender is not None: __handleSender(sender, msg)

        receiver = fipamessage.getElementsByTagName(RECEIVER)[0]
        if receiver is not None: __handleReceiver(receiver, msg)

        reply_to = fipamessage.getElementsByTagName(REPLY_TO)[0]
        if reply_to is not None: __handleReplyTo(reply_to, msg)

        content = fipamessage.getElementsByTagName(CONTENT)[0]
        if content is not None: __handleContent(content, msg)

        language = fipamessage.getElementsByTagName(LANGUAGE)[0]
        if language is not None: __handleLanguage(language, msg)

        encoding = fipamessage.getElementsByTagName(ENCODING)[0]
        if encoding is not None: __handleEncoding(encoding, msg)

        ontology = fipamessage.getElementsByTagName(ONTOLOGY)[0]
        if ontology is not None: __handleOntology(ontology, msg)

        protocol = fipamessage.getElementsByTagName(PROTOCOL)[0]
        if protocol is not None: __handleProtocol(protocol, msg)

        conversation_id = fipamessage.getElementsByTagName(CONVERSATION_ID)[0]
        if conversation_id is not None: __handleConversationId(conversation_id, msg)

        reply_with = fipamessage.getElementsByTagName(REPLY_WITH)[0]
        if reply_with is not None: __handleReplyWith(reply_with, msg)

        in_reply_to = fipamessage.getElementsByTagName(IN_REPLY_TO)[0]
        if in_reply_to is not None: __handleInReplyTo(in_reply_to, msg)

        reply_by = fipamessage.getElementsByTagName(REPLY_BY)[0]
        if reply_by is not None: __handleReplyBy(reply_by, msg)

    def __handleSender(sender, msg):
        print SENDER
        aid = AID()
        __handleAID(sender.getElementsByTagName("agent-identifier")[0], aid)
        msg.sender = aid

    def __handleAID(agent, aid):
        __handleName(agent.getElementsByTagName("name")[0], aid)
        __handleAddresses(agent.getElementsByTagName("addresses")[0], aid)
        #__handleResolvers(agent.getElementsByTagName("resolvers")[0], aid)
        #__handleUserDefined(agent.getElementsByTagName("user-defined")[0], aid)

    def __handleName(name, aid):
        print "name"
        id = name.getAttribute("id")
        print "id", id
        if id is None:
            id = name.getAttribute("refid")
            print "refid", id
        aid.name = id

    def __handleAddresses(addresses, aid):
        print "addresses"
        url = addresses.getElementsByTagName("url")
        for u in url:
            __handleURL(u, aid)

    def __handleURL(url, aid):
        print "url"
        href = url.getAttribute("href")
        print "href", href
        aid.addAddress(href)

    def __handleReceiver(receiver, msg):
        print RECEIVER
        for r in receiver.getElementsByTagName("agent-identifier"):
            aid = AID()
            __handleAID(r, aid)
            msg.receivers.add(aid)

    def __handleReplyTo(reply_to, msg):
        print REPLY_TO
        aid = AID()
        __handleAID(reply_to.getElementsByTagName("agent-identifier")[0], aid)
        msg.reply_to = aid

    def __handleContent(content, msg):
        print CONTENT
        href = content.getAttribute("href")
        print "href", href
        value = content.firstChild.nodeValue.strip()
        print value
        msg.content = value  # TODO: href

    def __handleLanguage(language, msg):
        print LANGUAGE
        href = language.getAttribute("href")
        print "href", href
        value = language.firstChild.nodeValue.strip()
        print value
        msg.language = value  # TODO: href

    def __handleEncoding(encoding, msg):
        print ENCODING
        href = encoding.getAttribute("href")
        print "href", href
        value = encoding.firstChild.nodeValue.strip()
        print value
        msg.encoding = value  # TODO: href

    def __handleOntology(ontology, msg):
        print ONTOLOGY
        href = ontology.getAttribute("href")
        print "href", href
        value = ontology.firstChild.nodeValue.strip()
        print value
        msg.ontology = value  # TODO: href

    def __handleProtocol(protocol, msg):
        print PROTOCOL
        href = protocol.getAttribute("href")
        print "href", href
        value = protocol.firstChild.nodeValue.strip()
        print value
        msg.protocol = value  # TODO: href

    def __handleConversationId(conversation_id, msg):
        print CONVERSATION_ID
        href = conversation_id.getAttribute("href")
        print "href", href
        value = conversation_id.firstChild.nodeValue.strip()
        print value
        msg.conversation_id = value  # TODO: href

    def __handleReplyWith(reply_with, msg):
        print REPLY_WITH
        href = reply_with.getAttribute("href")
        print "href", href
        value = reply_with.firstChild.nodeValue.strip()
        print value
        msg.reply_with = value  # TODO: href

    def __handleInReplyTo(in_reply_to, msg):
        print IN_REPLY_TO
        href = in_reply_to.getAttribute("href")
        print "href", href
        value = in_reply_to.firstChild.nodeValue.strip()
        print value
        msg.in_reply_to = value  # TODO: href

    def __handleReplyBy(reply_by, msg):
        print REPLY_BY
        time = reply_by.getAttribute("time")
        print "time", time
        href = reply_by.getAttribute("href")
        print "href", href
        msg.reply_by = time  # TODO: href

