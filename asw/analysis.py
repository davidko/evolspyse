import wx

from matplotlib.numerix import arange, sin, pi

import matplotlib

# uncomment the following to use wx rather than wxagg
#matplotlib.use('WX')
#from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas

# comment out the following to use wx rather than wxagg
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg 

from matplotlib.backends.backend_wx import _load_bitmap
from matplotlib.figure import Figure
from matplotlib.numerix.mlab import rand


class AnalysisFrame(wx.Frame):
    def __init__(self, parent, id, title, analyse_size):
        self.width, self.height = analyse_size
        wx.Frame.__init__(self, parent, id, title, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))

        self.SetBackgroundColour(wx.NamedColor("WHITE"))

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        
        self.axes.plot(t, s)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)

        # Capture the paint message
#        EVT_PAINT(self, self.OnPaint)        

#        self.toolbar = MyNavigationToolbar(self.canvas, True)
#        self.toolbar.Realize()
#        if wx.Platform == '__WXMAC__':
#            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
#            # having a toolbar in a sizer. This work-around gets the buttons
#            # back, but at the expense of having the toolbar at the top
#            self.SetToolBar(self.toolbar)
#        else:
#            # On Windows platform, default window size is incorrect, so set
#            # toolbar width to figure width.
#            tw, th = self.toolbar.GetSizeTuple()
#            fw, fh = self.canvas.GetSizeTuple()
#            # By adding toolbar in sizer, we are able to put it at the bottom
#            # of the frame - so appearance is closer to GTK version.
#            # As noted above, doesn't work for Mac.
#            self.toolbar.SetSize(wxSize(fw, th))
#            self.sizer.Add(self.toolbar, 0, wxLEFT | wxEXPAND)
#
#        # update the axes menu on the toolbar
#        self.toolbar.update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetSizer(self.sizer)
        self.Fit()
        
    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()
    
    def OnClose(self, event):
        self.Destroy()
