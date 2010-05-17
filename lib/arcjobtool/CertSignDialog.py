# -*- coding: utf-8 -*-
# generated by wxGlade HG on Wed Apr 21 15:10:35 2010

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

from CertUtils import CertificateRequest

class CertSignDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CertSignDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Certificate request text")
        self.certRequestText = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)
        self.emailFromLabel = wx.StaticText(self, -1, "From:")
        self.emailFromText = wx.TextCtrl(self, -1, "")
        self.caEmailLabel = wx.StaticText(self, -1, "CA/RA Email address (To):")
        self.caEmailText = wx.TextCtrl(self, -1, "")
        self.emailSubjectLabel = wx.StaticText(self, -1, "Subject:")
        self.emailSubjectText = wx.TextCtrl(self, -1, "Certificate request", style=wx.TE_READONLY)
        self.caNoteText = wx.TextCtrl(self, -1, "Please note that in some cases you should not send the certificate request to the specified CA email address instead to your registration RA. Please look at http://ca.nordugrid.org/ra.html for more information. If in doubt send it directly to the CA.", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.copyToClipboardButton = wx.Button(self, -1, "Copy to clipboard")
        self.sendRequestButton = wx.Button(self, -1, "Send")
        self.closeButton = wx.Button(self, -1, "Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onCopyToClipboard, self.copyToClipboardButton)
        self.Bind(wx.EVT_BUTTON, self.onSendRequest, self.sendRequestButton)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: CertSignDialog.__set_properties
        self.SetTitle("Send Certificate signing request")
        self.SetSize((616, 438))
        self.certRequestText.SetFont(wx.Font(10, wx.SCRIPT, wx.NORMAL, wx.NORMAL, 0, "Courier"))
        self.emailFromLabel.SetMinSize((200, -1))
        self.caEmailLabel.SetMinSize((200, -1))
        self.emailSubjectLabel.SetMinSize((200, -1))
        self.emailSubjectText.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        self.caNoteText.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_INFOBK))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CertSignDialog.__do_layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        buttonRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        emailSubjectSizer = wx.BoxSizer(wx.HORIZONTAL)
        caEmailSizer = wx.BoxSizer(wx.HORIZONTAL)
        emailFromSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.label_1, 0, wx.LEFT|wx.RIGHT|wx.TOP, 4)
        mainSizer.Add(self.certRequestText, 4, wx.ALL|wx.EXPAND, 4)
        emailFromSizer.Add(self.emailFromLabel, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 4)
        emailFromSizer.Add(self.emailFromText, 1, wx.LEFT|wx.RIGHT|wx.TOP, 4)
        mainSizer.Add(emailFromSizer, 0, wx.EXPAND, 0)
        caEmailSizer.Add(self.caEmailLabel, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 4)
        caEmailSizer.Add(self.caEmailText, 1, wx.LEFT|wx.RIGHT|wx.TOP, 4)
        mainSizer.Add(caEmailSizer, 0, wx.EXPAND, 0)
        emailSubjectSizer.Add(self.emailSubjectLabel, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 4)
        emailSubjectSizer.Add(self.emailSubjectText, 1, wx.LEFT|wx.RIGHT|wx.TOP, 4)
        mainSizer.Add(emailSubjectSizer, 0, wx.EXPAND, 0)
        mainSizer.Add(self.caNoteText, 0, wx.ALL|wx.EXPAND, 4)
        buttonRowSizer.Add(self.copyToClipboardButton, 0, wx.ADJUST_MINSIZE, 0)
        buttonRowSizer.Add(self.sendRequestButton, 0, 0, 0)
        buttonRowSizer.Add(self.closeButton, 0, 0, 0)
        mainSizer.Add(buttonRowSizer, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 4)
        self.SetSizer(mainSizer)
        self.Layout()
        self.Centre()
        # end wxGlade

        self.__initDialog()
        
    def __initDialog(self):
        """
        Initiate dialog instance variables.
        """
        self.__certRequest = None
        
    def __updateControls(self):
        """
        Update user interface controls.
        """
        requestFile = open(self.__certRequest.certRequestFilename, "r")
        certRequestString = requestFile.read()
        requestFile.close()
        self.certRequestText.SetValue(certRequestString)
        self.caEmailText.SetValue(self.__certRequest.CAEmail)
        self.emailSubjectText.SetValue(self.__certRequest.emailSubject)
        self.emailFromText.SetValue(self.__certRequest.email)
        
    def setCertRequest(self, request):
        """
        Assigne CertRequest instance.
        """
        self.__certRequest = request
        self.__updateControls()
        
    def getCertRequest(self):
        """
        Return CertRequest instance.
        """
        return self.__certRequest

    def onSendRequest(self, event): # wxGlade: CertSignDialog.<event_handler>
        """
        Send signing request.
        """
        
        self.__certRequest.emailSMTPServer = wx.GetTextFromUser("Enter outgoing mailserver", "Certificate request", self.__certRequest.emailSMTPServer)
        
        if self.__certRequest.emailSMTPServer == "":
            wx.MessageBox("Empty string for outgoing mail server given.", "Certificate request")
            return
        
        self.__certRequest.emailTo = self.caEmailText.GetValue()
        self.__certRequest.emailFrom = self.emailFromText.GetValue()

        errorMessage = self.__certRequest.sendSigningRequest()
        
        if errorMessage == "":
            wx.MessageBox("Certificate request sent")
            self.Close()
        else:
            wx.MessageBox(errorMessage)

    def onClose(self, event): # wxGlade: CertSignDialog.<event_handler>
        """
        Close dialog.
        """
        self.Close()
        
    def onCopyToClipboard(self, event): # wxGlade: CertSignDialog.<event_handler>
        """
        Copy certificate request text to clipboard.
        """
        self.certRequestText.SetSelection(-1, -1)
        self.certRequestText.Copy()
        wx.MessageBox("Certificate request text has been copied to the clipboard.", "Certificate request")
        
    certRequest = property(getCertRequest, setCertRequest)
    


# end of class CertSignDialog


