"""Spyse Tkinter UI agent module"""

from spyse.core.agents.ui import UIAgent
from spyse.core.content.content import ACLMessage

from Tkinter import *


class TkinterAgent(UIAgent):
    """A Tkinter UI agent"""
    # http://www.python.org/topics/tkinter/

    # the next two lines of code need to be commented out for epydoc to work
    __root = Tk()
    __root.withdraw()

    def __init__(self, name, mts, **namedargs):
        super(TkinterAgent, self).__init__(name, mts, **namedargs)
        #self.__root = Tk()
#        if not hasattr(self, '__root'):
#            self.__root = Tk()
#            self.__root.title("Root")
        #self.__root.withdraw() # won't need this
            #self.__root.mainloop()
#        setattr(self, '__root', Tk())
        self.top = Toplevel(self.__root)
        self.top.title(name)
        #self.top.protocol("WM_DELETE_WINDOW", self.top.destroy)
        self.create_widgets(self.top)

    def make_Tk(root):
        root.title("Spyse Agent Management System")
        title_label = Label(root)
        title_label["text"]="Spyse - Agent Management System"
        title_label.pack()
        quit_button = Button(root, command=quit) # doesn't work
        quit_button["text"]="Quit"
        quit_button.pack()
        #root.withdraw()

    def create_widgets(self, frame):
        # Override
        pass

    def take_down(self):
        print "destroying toplevel"
        #self.top.destroy()
        # TODO: is there a better way to kill windows ??? 

    @classmethod
    def run_GUI(cls):
        cls.__root.mainloop()
#    run_GUI = classmethod(run_GUI)

