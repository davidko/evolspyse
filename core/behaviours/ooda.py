"""Spyse OODA behaviour module"""

import time

# http://www.mindsim.com/MindSim/Corporate/OODA.html
# http://www.d-n-i.net/second_level/boyd_military.htm
# http://www.belisarius.com/modern_business_strategy/boyd/essence/eowl_frameset.htm
# http://www.valuebasedmanagement.net/methods_boyd_ooda_loop.html
# http://www.fastcompany.com/magazine/59/pilot.html
#
# The OODA loop (Observe, Orient, Decide, and Act) is an
# information strategy concept for information warfare
# developed by Colonel John Boyd (1927-1997). Although the
# OODA model was clearly created for military purposes,
# elements of the same theory can also be applied to business
# strategy. Boyd developed the theory based on his earlier
# experience as a fighter pilot and work on energy maneuverability.
# He initially used it to explain victory in air-to-air combat,
# but in the last years of his career he expanded his OODA loop
# theory into a grand strategy that would defeat an enemy
# strategically by pychological paralysis.

from spyse.core.behaviours.fsm import FSMBehaviour


class Observation(object):
    pass


class Orientation(object):
    pass


class Decision(object):
    pass


class Action(object):
    pass


class OODABehaviour(FSMBehaviour):
    pass

