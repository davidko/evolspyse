"""Spyse agent basic behaviour module"""

import time
from datetime import datetime
import threading

from spyse.core.content.content import ACLMessage


class Behaviour(object):
    """The basic behaviour class of spyse agents"""

    def __init__(self, name='', paused=False, **namedargs):
        self.name = name
        self.__agent = None  # Set later
        self.__result = None
        self.__done = False
        self.__paused = paused
        self.setup(**namedargs)

    def setup(self):
        # Override this for extra initialisation
        pass

    def action(self):
        # Override in subclasses with specific behaviour
        print 'Default action'
        self.set_done()

    def take_down(self):
        # Override in subclasses with specific behaviour
        pass

    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False
    
    def paused(self):
        return self.__paused

    def _get_agent(self):
        # Overridden in CompositeBehaviour
        return self.__agent

    def _set_agent(self, agent):
        # Overridden in CompositeBehaviour
        self.__agent = agent

    def __get_agent(self): return self._get_agent()
    def __set_agent(self, agent): self._set_agent(agent)
    agent = property(__get_agent, __set_agent, None, "the agent whose behaviour this is")

    def _get_result(self):
        """Return result, but only once"""
        # FSMBehaviour currently relies on result being cleared
        result = self.__result
        self.__result = None
        return result

    def _set_result(self, result):
        """Set result"""
        # Overridden in fsm demo
        self.__result = result

    def __get_result(self): return self._get_result()
    def __set_result(self, result): self._set_result(result)
    result = property(__get_result, __set_result, None, "the result of this behaviour")

    def set_done(self):
        self.__done = True

    def done(self):
        return self.__done

    def sleep(self, s):
        #print 'Behaviour', self.name, 'sleeping for', s, 'seconds'
        time.sleep(s)


class TickerBehaviour(Behaviour):
    """A behaviour that performs repeatedly after a fixed interval."""
    def __init__(self, name='', period=10, **namedargs):
        self.period = period
        self.__wakeup = time.time()  # + self.period   # start immediately
        self.tick_count = 0
        super(TickerBehaviour, self).__init__(name, **namedargs)

    def action(self):
        self.on_action()   # give subclasses a chance to work in between ticks

        if self.done() is False:
            block_time = self.__wakeup - time.time()
            if block_time <= 0:
                # Timeout is expired --> execute the user defined action and
                # re-initialize wakeup
                self.tick_count = self.tick_count + 1
                self.on_tick()
                self.__wakeup = time.time() + self.period

    def on_action(self):
        # Override this in subclasses with custom action
        pass

    def on_tick(self):
        # Override this in subclasses with ticking behaviour
        pass


class StepperBehaviour(Behaviour):
    """A behaviour where all instances of the same class are
       performed during a single step.

       Used for synchronous simulation.
    
       EXPERIMENTAL.  May disappear in the future.
    """

    # The number of instances of this behaviour class
    _count = 0

    # The number of instances finished with this step
    _done = 0

    # The next step
    _nextstep = 1

    def __init__(self, name='', **namedargs):
        self.__class__._count += 1
        self.step = 0
        super(StepperBehaviour, self).__init__(name, **namedargs)
 
    # Don't override action().  Instead, override the methods below.
    def action(self):
        # Take next step when all instances are done with the current step.
        # FIXME: Class variables need to be protected with locks
        if self.__class__._done >= self.__class__._count:
            self.__class__._nextstep += 1
            self.__class__._done = 0
            self.start_step()
        if self.step < self.__class__._nextstep:
            self.do_step()
        else:
            self.dont_step()

    def set_step_done(self):
        # Don't override
        self.step += 1
        self.__class__._done += 1
        self.done_step()
    
    def set_done(self):
        self.__class__._count -= 1
        super(StepperBehaviour, self).set_done()

    def start_step(self):
        """Start the step."""
        # Override
        print datetime.now(), "Starting step", self.__class__._nextstep - 1

    def do_step(self):
        """Called during the step."""
        # Override
        print datetime.now(), "Agent", self.agent.name, "doing some work in step", str(self.step) + "."

    def dont_step(self):
        """Called when waiting for the next step."""
        # Override
        print datetime.now(), "Agent", self.agent.name, "waiting for next step."

    def done_step(self):
        """Done the step."""
        # Override
        print datetime.now(), "Agent", self.agent.name, "done with step", str(self.__class__._nextstep - 1) + '.'

class ReceiveBehaviour(Behaviour):
    def __init__(self, name='', template=None, **namedargs):
        self.__template = template
        super(ReceiveBehaviour, self).__init__(name, **namedargs)

    def action(self):
        # Do not override
        msg = self.agent.get_message(self.__template)
        if msg is not None:
            self.handle_message(msg)

    def handle_message(self, message):
        # Override
        print 'ReceiveBehaviour handling message, override this!'


class SendBehaviour(Behaviour):
    def __init__(self, name='', performative=None, receivers=None, content=None, **namedargs):
        self.performative = performative
        if receivers is None:
            self.receivers = []
        else:
            self.receivers = receivers
        self.content = content
        super(SendBehaviour, self).__init__(name, **namedargs)

    def action(self):
        msg = ACLMessage(self.performative)
        msg.receivers = self.receivers
        msg.content = self.content
        msg.set_conversation_id()

        # TODO: send message through MTS
        a = self.agent.send_message(msg)
        self.set_done()


class ThreadBehaviour(threading.Thread):
    """A behaviour running in its own thread."""

    # probably won't work like this, expect some synchronisation errors...
    # not tested

    def __init__(self, name='', behaviour=None, **namedargs):
        assert isinstance(behaviour, Behaviour), "Trying to add an object that is not a Behaviour"
        self.__behaviour = behaviour
        super(ThreadBehaviour, self).__init__(name, **namedargs)

    def run(self):
        while True:
            # run the behaviour, executing its action()
            if self.__behaviour is not None:
                self.__behaviour.action()
                if self.__behaviour.done():
                    break
            else:
                break
            time.sleep(0.1) # prevent system to run at maximum load
