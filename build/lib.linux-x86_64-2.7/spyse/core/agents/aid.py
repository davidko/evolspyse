"""Spyse agent ID module"""

from spyse.core.platform.hap import HAP
import random


class AID(object):

    AT = '@'

    """Agent IDentifier as specified by FIPA"""
    def __init__(self, name=None, shortname=None, hap=None):
        self.addresses = []
        self.hap = hap
        if name is None:
            if shortname is None:
                self.__shortname = 'Agent_%d' % random.randint(0, 1000000)
            else:
                self.__shortname = shortname
        elif isinstance(name, str):
            if shortname is not None:
                raise ValueError, "should not specify both name and shortname"
            a = name.split(AID.AT)
            self.__shortname = a[0]
            # If name contains an "@..." part then make a HAP from it
            # unless the hap argument was given
            if hap is None and len(a) > 1:
                self.hap = HAP(a[1])
#        elif isinstance(name, AID):
#            # Make me a copy of it
#            self.name = name.name
        else:
            raise TypeError, "name is of wrong type"

    def __cmp__(self, other):
        # Compare AIDs based on their string representations
        # Note:
        #    AID('foo:bar') == AID('foo:bar')
        # yields True, but
        #    AID('foo:bar') is AID('foo:bar')
        # yields False

        self_name = self.name
        other_name = other.name
        if self_name < other_name:
            return -1
        elif self_name == other_name:
            return 0
        elif self_name > other_name:
            return 1
        else:
            raise


    #
    # name functions
    #

    def __get_name(self):
        if self.hap is None:
            return self.__shortname
        else:
            return self.__shortname + AID.AT + self.hap.name

    def __set_name(self, name):
        assert isinstance(name, str), "Trying to set name that is not of type str"
        if AID.AT in name:
            a = name.split(AID.AT)
            self.__shortname = a[0]
            self.hap = HAP(a[1])
        else:
            self.__shortname = name
            # Leave HAP unchanged

    name = property(__get_name, __set_name, None, "name of this AID")

    def __get_shortname(self):
        return self.__shortname

    def __set_shortname(self, shortname):
        assert isinstance(shortname, str), "Trying to set shortname that is not of type str"
        assert not AID.AT in shortname, "Trying to set shortname containing at-sign"
        self.__shortname = shortname

    shortname = property(__get_shortname, __set_shortname, None, "shortname portion of this AID")

    def add_address(self, address):
        self.addresses.append(address)

    #resolvers
    #user_data

    def __repr__(self):
        if self.hap is None or self.hap.name is None:
            return "<AID " + self.__shortname + ">"
        else:
            return "<AID " + self.__shortname + AID.AT + self.hap.name + ">"

