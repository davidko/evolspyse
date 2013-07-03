"""Spyse HAP module"""

import random


class HAP(object):
    """Home Agent Platform identifier as specified by FIPA"""

    COLON = ':'

    def __init__(self, name=None, host=None, port=None):
        self.port = port
        if name is None:
            if host is None:
                self.host = 'Platform_%d' % random.randint(0, 1000000)
            else:
                self.host = host
        else:
            if host is None:
                a = name.split(HAP.COLON)
                self.host = a[0]
                # If name contains an ":..." part then take port from that
                # unless the port argument was given
                if port is None and len(a) > 1:
                    self.port = a[1]
            else:
                raise ValueError, "cannot specify both name and host"


    def __cmp__(self, other):
        # Compare HAPs based on their string representations
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
        if self.port is None:
            return self.host
        else:
            return self.host + HAP.COLON + self.port

    def __set_name(self, name):
        assert isinstance(name, str), "Trying to set a name that is not of type str"
        if HAP.COLON in name:
            a = name.split(HAP.COLON)
            self.host = a[0]
            self.port = a[1]
        else:
            self.host = name
            # Leave port unchanged

    name = property(__get_name, __set_name, None, "name of this HAP")

    def __repr__(self):
        if self.port is None:
            return "<HAP " + self.host + ">"
        else:
            return "<HAP " + self.host + HAP.COLON + self.port + ">"

