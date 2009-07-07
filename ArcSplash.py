# -*- coding: iso-8859-15 -*-
# generated by wxGlade HG on Fri Jul  3 20:15:50 2009

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

import os

class ArcSplash(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ArcSplash.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.splashBitmap = wx.StaticBitmap(self, -1, wx.Bitmap("/sw/laportal/arcgui/images/ARClogo.png", wx.BITMAP_TYPE_ANY))
        self.label_5 = wx.StaticText(self, -1, "ArcGUI - 0.1\nGraphical User Interface Client for ARC\nCopyright (C) 2009\nLunarc, Lund University")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.__initWindow()

    def __set_properties(self):
        # begin wxGlade: ArcSplash.__set_properties
        self.SetTitle("About ArcGUI")
        self.SetSize((248, 389))
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.splashBitmap.SetMinSize((245, 324))
        self.label_5.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.label_5.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ArcSplash.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.splashBitmap, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(self.label_5, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 3)
        self.SetSizer(sizer_2)
        self.Layout()
        self.Centre()
        # end wxGlade
        
    def __initWindow(self):
        if os.environ.has_key("ARCGUI_LOCATION"):
            arcGuiLocation = os.environ["ARCGUI_LOCATION"]
            if os.path.exists(arcGuiLocation):
                self.splashBitmap.SetBitmap(wx.Bitmap(os.path.join(arcGuiLocation,"images/ARClogo.png"), wx.BITMAP_TYPE_ANY))

# end of class ArcSplash

