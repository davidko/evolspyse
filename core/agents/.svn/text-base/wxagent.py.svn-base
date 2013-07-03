"""Spyse wxPython UI agent module"""

import wx

from spyse.core.agents.ui import UIAgent
from spyse.core.content.content import ACLMessage


class ManagementInterface(wx.Frame):
    def __init__(self):
        super(ManagementInterface, self).__init__(None, -1, "Agent Manager", size=(400, 400))
        # create frame with AMS/DF/Sniffer interface


class wxAgent(UIAgent):
    """A wxPython UI agent"""
    # http://www.wxpython.org/

    __root = wx.PySimpleApp()
    #__root = wx.App()   # captures stdout/stderr

#    __manager = None
#    interface = False

    def setup(self, size=None):
        if size is not None:
            width = size[0]
            height = size[1]
        else:
            width = 400
            height = 400
        self.frame = wxAgentFrame(None, -1, self.name, position=(10, 10), size=(width, height))
        self.create_widgets(self.frame)
        self.frame.Show(True)

    def create_ManagementInterface(self):
        if self.__manager is not None:
            return None
        if self.interface is True:
            return ManagementInterface(wx.Frame(None, -1, self.name, size=(400, 400)))
        else:
            return None

    #create_ManagementInterface()

    def create_widgets(self, frame):
        # Override
        frame.window = wx.Panel(frame)

    @classmethod
    def run_GUI(cls):
        cls.__root.MainLoop()

# FIXME:
#    def shutdown(self, e):
#        print 'EXIT'
#        self.frame.Close(True)


class wxAgentFrame(wx.Frame):
    def __init__(self, parent, id, title, position, size):
        super(wxAgentFrame, self).__init__(parent, id, title, position, size)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.Destroy()
        self.closed()
        #sys.exit()
        
    def closed(self):
        # Overwrite if needed
        pass
       

# wx Window Hierarchy (partial)
#
#object
#    _core.Object
#    glcanvas.GLContext
#        _core.EvtHandler
#            _core.Window
#                glcanvas.GLCanvas
#                _windows.StatusBar
#                _windows.Panel
#                    _windows.ScrolledWindow
#                _windows.TopLevelWindow
#                    _windows.Dialog
#                    _windows.Frame
#                        _windows.SplashScreen



'''
Bob,
 
Hierbij de info tegen de screen flicker:
 
Groet, Jeroen.
--------------------------------------------------------------------------
        # in de __init__ van de main_view (draw_panel is hetgeen waarop getekend wordt.)
 
        self.draw_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.draw_panel.Bind(wx.EVT_PAINT, self.on_paint)
--------------------------------------------------------------------------
        # methoden:
    def on_erase_background(self, event):
        """ on_erase_background
            This function does nothing, and does so on purpose:
            it prevents screen flicker in MS Windows
        """
        pass
 

    def on_paint(self, event):
        """ on_paint """
        # make a buffered device context
        device_context = BufferedPaintDC(self.draw_panel)
        self.draw_panel.PrepareDC(device_context)
        device_context.BeginDrawing()
 
        # do your thing
 
        device_context.EndDrawing()
--------------------------------------------------------------------------
 
 
'''
