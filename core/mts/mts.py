"""Spyse Message Transport System module"""

import threading
import copy
import socket 
import string
import pickle
import Pyro4.core

from spyse.core.agents.aid import AID
from spyse.core.content.content import ACLMessage

class MTS():

    def __init__(self, hap, nameserver):
        self.hap = hap
        self.pyrouri = None  # Gets set by platform
        self.ams = None      # Gets set by platform
        self.__nameserver = nameserver

    def send(self, sender, msg):
        """Send message"""
        new_msg = copy.deepcopy(msg.encode_ACL())
        new_msg.sender = sender

        # The send method should return True or False so the agent
        # knows if the message is successfully delivered
        res = False
        for rec in msg.receivers:
            res = self.__deliver_to(new_msg, rec)
        return res

    def __deliver_to(self, new_msg, rec):
        new_msg.receivers = [rec]
        rec_hap = rec.hap
        if rec_hap is None:
            rec_hap = self.hap
        if (rec_hap == self.hap):
            # Local delivery
            if self.ams is None:
                raise Exception("Cannot deliver message because ams is not set")
            rec_aid = self.ams.find_agent(rec.shortname)
            if rec_aid is None:
                print 'Could not deliver message to', rec.name + ': receiver not found.'
                return False
            rec_addresses = rec_aid.addresses
            if len(rec_addresses) > 0:
                rec_adr = rec_addresses[0]
                if rec_adr == self.pyrouri:
                    return self.__receive(new_msg)
                else:
                    return Pyro4.core.getProxyForURI(rec_adr)._receive_global_msg(new_msg)
            else:
                return self.__receive(new_msg)
        else:
            # Remote delivery
            new_msg.sender.hap = self.hap

            try:
                if rec_hap.ns_lookup:
                    print('Looking up ns name: {0}'.format(rec_hap.name))
                    uri = self.__nameserver.lookup(rec_hap.name)
                else:
                    uri = "PYRO:" + "mts@" + rec_hap.name 
                    print('URI : {0}'.format(uri))
                remote_mts = Pyro4.Proxy(uri)
                try:
                    return remote_mts._receive_global_msg(new_msg)
                except Exception, e:
                    print 'Could not deliver message to', rec.name + ': remote mts', mts_string, "raised error:", e
                    return False
            except socket.error, errmsg:
                print 'Could not deliver message to', rec.name + ': error with remote MTS.'
                print errmsg
                return False
            except Exception as e:
                print 'Could not deliver message to', rec.name + ': ' + str(e)
                return False

    def __receive(self, msg):
        for rec in msg.receivers:
            agent = self.ams.get_agent(rec.shortname)
            if agent:
                agent.receive_message(copy.deepcopy(msg.encode_ACL()))
                return True
            else:
                print 'MTS: Could not find receiving agent', rec.shortname
                return False

    def _receive_global_msg(self, msg):
        return self.__receive(msg)

