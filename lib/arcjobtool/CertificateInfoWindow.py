# -*- coding: iso-8859-15 -*-
# generated by wxGlade HG on Tue May 19 21:48:13 2009

#
# CertificateInfoWindow window class
#

"""
Implements the the arcgui certificate information window.
"""

# -*- coding: iso-8859-15 -*-
# generated by wxGlade HG on Mon Jul  6 16:28:42 2009

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

import arc

EVT_CERTINFO_CLOSE_TYPE = wx.NewEventType()
EVT_CERTINFO_CLOSE = wx.PyEventBinder(EVT_CERTINFO_CLOSE_TYPE, 1)

class CertInfoCloseEvent(wx.PyCommandEvent):
    """
    Event sent by worker threads to update progress.
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)

class CertificateInfoWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CertificateInfoWindow.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_2 = wx.Panel(self, -1)
        self.notebook_1 = wx.Notebook(self.panel_2, -1, style=0)
        self.proxyPane = wx.Panel(self.notebook_1, -1)
        self.certPane = wx.Panel(self.notebook_1, -1)
        self.dnLabel = wx.StaticText(self.certPane, -1, "DN")
        self.dnText = wx.TextCtrl(self.certPane, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_LINEWRAP)
        self.notBeforeLabel = wx.StaticText(self.certPane, -1, "Not before")
        self.notBeforeText = wx.TextCtrl(self.certPane, -1, "")
        self.notAfterLabel = wx.StaticText(self.certPane, -1, "Not after")
        self.notAfterText = wx.TextCtrl(self.certPane, -1, "")
        self.proxyRemainingLabel = wx.StaticText(self.proxyPane, -1, "Remaining")
        self.proxyRemainingText = wx.TextCtrl(self.proxyPane, -1, "")
        self.proxyNotBeforeLabel = wx.StaticText(self.proxyPane, -1, "Not before")
        self.proxyNotBeforeText = wx.TextCtrl(self.proxyPane, -1, "")
        self.proxyNotAfterLabel = wx.StaticText(self.proxyPane, -1, "Not after")
        self.proxyNotAfterText = wx.TextCtrl(self.proxyPane, -1, "")
        self.closeButton = wx.Button(self.panel_2, -1, "Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
        # end wxGlade
        
        self.__initWindow()

    def __set_properties(self):
        # begin wxGlade: CertificateInfoWindow.__set_properties
        self.SetTitle("Certificate information")
        self.SetSize((432, 324))
        self.dnLabel.SetMinSize((120, -1))
        self.dnText.SetMinSize((-1, 54))
        self.notBeforeLabel.SetMinSize((120, -1))
        self.notBeforeText.SetMinSize((-1, 27))
        self.notAfterLabel.SetMinSize((120, -1))
        self.notAfterText.SetMinSize((-1, 27))
        self.proxyRemainingLabel.SetMinSize((120, -1))
        self.proxyRemainingText.SetMinSize((-1, 27))
        self.proxyNotBeforeLabel.SetMinSize((120, -1))
        self.proxyNotBeforeText.SetMinSize((-1, 27))
        self.proxyNotAfterLabel.SetMinSize((120, -1))
        self.proxyNotAfterText.SetMinSize((-1, 27))
        self.notebook_1.SetMinSize((422, 272))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CertificateInfoWindow.__do_layout
        sizer_20 = wx.BoxSizer(wx.VERTICAL)
        sizer_21 = wx.BoxSizer(wx.VERTICAL)
        sizer_22 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_23_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_27_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_26_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_24_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_23 = wx.BoxSizer(wx.VERTICAL)
        sizer_27 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_26 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_24 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_24.Add(self.dnLabel, 0, 0, 0)
        sizer_24.Add(self.dnText, 1, wx.EXPAND, 0)
        sizer_23.Add(sizer_24, 0, wx.ALL|wx.EXPAND, 4)
        sizer_26.Add(self.notBeforeLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_26.Add(self.notBeforeText, 1, wx.EXPAND, 0)
        sizer_23.Add(sizer_26, 0, wx.ALL|wx.EXPAND, 4)
        sizer_27.Add(self.notAfterLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_27.Add(self.notAfterText, 1, wx.EXPAND, 0)
        sizer_23.Add(sizer_27, 0, wx.ALL|wx.EXPAND, 4)
        self.certPane.SetSizer(sizer_23)
        sizer_24_copy.Add(self.proxyRemainingLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_24_copy.Add(self.proxyRemainingText, 1, wx.EXPAND, 0)
        sizer_23_copy.Add(sizer_24_copy, 0, wx.ALL|wx.EXPAND, 4)
        sizer_26_copy.Add(self.proxyNotBeforeLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_26_copy.Add(self.proxyNotBeforeText, 1, wx.EXPAND, 0)
        sizer_23_copy.Add(sizer_26_copy, 0, wx.ALL|wx.EXPAND, 4)
        sizer_27_copy.Add(self.proxyNotAfterLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_27_copy.Add(self.proxyNotAfterText, 1, wx.EXPAND, 0)
        sizer_23_copy.Add(sizer_27_copy, 0, wx.ALL|wx.EXPAND, 4)
        self.proxyPane.SetSizer(sizer_23_copy)
        self.notebook_1.AddPage(self.certPane, "Certificate")
        self.notebook_1.AddPage(self.proxyPane, "Proxy")
        sizer_21.Add(self.notebook_1, 1, wx.ALL|wx.EXPAND, 5)
        sizer_22.Add(self.closeButton, 0, 0, 0)
        sizer_21.Add(sizer_22, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.panel_2.SetSizer(sizer_21)
        sizer_20.Add(self.panel_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_20)
        self.Layout()
        self.Centre()
        # end wxGlade
        
    def __initWindow(self):
        """
        Custom window initialisation routine. Binds EVT_CLOSE to
        onCloseWindow and initalises class variables.
        """
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        self.__userConfig = None
        
    def onCloseWindow(self, event):
        """
        Handles a window close event notifying parent window that
        the window is destroyed/closed.
        """
        evt = CertInfoCloseEvent(EVT_CERTINFO_CLOSE_TYPE, -1)
        wx.PostEvent(self.GetParent(), evt)
        self.Destroy()

    def onClose(self, event): # wxGlade: CertificateInfoWindow.<event_handler>
        """
        Event method for handling the close button.
        """
        self.Close()
        
    def setUserConfig(self, userConfig):
        """
        Handles the assignment of the userConfig property. Fills the
        text boxes with relevant information
        """
        self.__userConfig = userConfig
        
        # Get certificate and proxy locations
        
        proxyPath = str(self.__userConfig.ProxyPath())
        userCertPath = str(self.__userConfig.CertificatePath())
        userKeyPath = str(self.__userConfig.KeyPath())
        
        # Update user certificate information
        
        credential = arc.Credential(userCertPath, "", "", "")
        self.dnText.SetValue(credential.GetDN())
        self.notBeforeText.SetValue(str(credential.GetStartTime()))
        self.notAfterText.SetValue(str(credential.GetEndTime()))
        
        # Update user proxy certificate information.
        
        credential = arc.Credential(proxyPath, "", "", "")
        self.proxyNotBeforeText.SetValue(str(credential.GetStartTime()))
        self.proxyNotAfterText.SetValue(str(credential.GetEndTime()))
        self.proxyRemainingText.SetValue(str(credential.GetEndTime()-arc.Time()))        
        
    def getUserConfig(self):
        """
        Returns the current value of the userConfig property.
        """
        return self.__userConfig
    
    userConfig = property(getUserConfig, setUserConfig)
        
# end of class CertificateInfoWindow


