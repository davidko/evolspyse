#!/usr/bin/env python

from spyse.core.agents.agent import Agent
from spyse.aaapl.aaapl import AAAPLBehaviour
from spyse.app.app import App

class AAAPLAgent(Agent):
    def setup(self):
        print "AAAPLAgent.setup"
        self.add_behaviour(AAAPLBehaviour(filename='spyse/demo/aaapl/runsquare.3apl'))

class MyApp(App):
    # Customize the App class by overriding run()
    def run(self, args):
        self.start_agent(AAAPLAgent)

if __name__ == "__main__":
    MyApp()

