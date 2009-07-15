# -*- coding: iso-8859-15 -*-
# generated by wxGlade HG on Mon Jul  6 19:39:07 2009

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

import arc

class DefaultServicesDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DefaultServicesDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.defaultServicesList = wx.ListBox(self, -1, choices=[])
        self.addServiceButton = wx.Button(self, -1, "Add...")
        self.modifyServiceButton = wx.Button(self, -1, "Modify...")
        self.removeServiceButton = wx.Button(self, -1, "Remove")
        self.clearServicesButton = wx.Button(self, -1, "Clear")
        self.okButton = wx.Button(self, wx.ID_OK, "")
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onAddService, self.addServiceButton)
        self.Bind(wx.EVT_BUTTON, self.onModifyService, self.modifyServiceButton)
        self.Bind(wx.EVT_BUTTON, self.onRemoveService, self.removeServiceButton)
        self.Bind(wx.EVT_BUTTON, self.onClearServices, self.clearServicesButton)
        # end wxGlade
        
        self.__initDialog()

    def __set_properties(self):
        # begin wxGlade: DefaultServicesDialog.__set_properties
        self.SetTitle("Default services")
        self.SetSize((457, 315))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DefaultServicesDialog.__do_layout
        sizer_28 = wx.BoxSizer(wx.VERTICAL)
        sizer_31 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_29 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_30 = wx.BoxSizer(wx.VERTICAL)
        sizer_29.Add(self.defaultServicesList, 1, wx.ALL|wx.EXPAND, 4)
        sizer_30.Add(self.addServiceButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_30.Add(self.modifyServiceButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_30.Add(self.removeServiceButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_30.Add(self.clearServicesButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_29.Add(sizer_30, 0, wx.ALL|wx.EXPAND, 4)
        sizer_28.Add(sizer_29, 1, wx.EXPAND, 0)
        sizer_31.Add(self.okButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_31.Add(self.cancelButton, 0, wx.ADJUST_MINSIZE, 0)
        sizer_28.Add(sizer_31, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 4)
        self.SetSizer(sizer_28)
        self.Layout()
        self.Centre()
        # end wxGlade
        
    def __initDialog(self):
        self.__userConfig = None
        
    def setUserConfig(self, userConfig):
        """
        text boxes with relevant information
        """
        self.__userConfig = userConfig
        
        self.defaultServicesList.Clear()
        
        services = self.__userConfig.ConfTree().Get("DefaultServices")
        for i in range(services.Size()):
            self.defaultServicesList.Append(str(services.Child(i)))
            url = arc.URL(str(services.Child(i)))
                        
    def getUserConfig(self):
        """
        Returns the current value of the userConfig property.
        """
        return self.__userConfig
    
    userConfig = property(getUserConfig, setUserConfig)

    def onAddService(self, event): # wxGlade: DefaultServicesDialog.<event_handler>
        serviceUrl = wx.GetTextFromUser("Add new service", "Default services", "", centre = True)
        if serviceUrl!="":
            url = arc.URL(str(serviceUrl))
            if url.toBool() == True:
                self.defaultServicesList.Append(serviceUrl)
            else:
                wx.MessageBox("Not a valid URL", "Default services")

    def onRemoveService(self, event): # wxGlade: DefaultServicesDialog.<event_handler>
        if self.defaultServicesList.GetSelection()>=0:
            self.defaultServicesList.Delete(self.defaultServicesList.GetSelection())
        else:
            wx.MessageBox("Please select a service in the list.")

    def onClearServices(self, event): # wxGlade: DefaultServicesDialog.<event_handler>
        self.defaultServicesList.Clear()

    def onModifyService(self, event): # wxGlade: DefaultServicesDialog.<event_handler>
        selectedItem = self.defaultServicesList.GetSelection()
        serviceUrl = self.defaultServicesList.GetString(selectedItem)
        serviceUrl = wx.GetTextFromUser("Modify service", "Default services", serviceUrl, centre = True)
        if serviceUrl!="":
            url = arc.URL(str(serviceUrl))
            if url.toBool() == True:
                self.defaultServicesList.SetString(selectedItem, serviceUrl)
            else:
                wx.MessageBox("Not a valid URL", "Default services")
                
    def getServiceList(self):
        return self.defaultServicesList.GetStrings()
                
    serviceList = property(getServiceList)

# end of class DefaultServicesDialog


