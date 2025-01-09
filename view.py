import wx
from constants import *

class View(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Busy Light Control Panel", size=(300, 200))
        self.controller = controller

        # Panel and layout
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.mode_label = wx.StaticText(panel, label="", size=(300, 25))
        vbox.Add(self.mode_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.color_label = wx.StaticText(panel, label="", size=(300, 25))
        vbox.Add(self.color_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.auto_color_label = wx.StaticText(panel, label="", size=(300, 25))
        vbox.Add(self.auto_color_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.dropdown = wx.Choice(panel, choices=[AUTOMATIC, OFF, "Red", "Green", "Blue", "Yellow", "Purple"])
        vbox.Add(self.dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        self.dropdown.Bind(wx.EVT_CHOICE, self.on_mode_change)
        panel.SetSizer(vbox)
        self.Show()

    def update_labels(self, mode, color, auto_color):
        self.mode_label.SetLabel(f"Mode: {mode}")
        self.color_label.SetLabel(f"Color: {self.convert_color_name(color)}")
        self.auto_color_label.SetLabel(f"AutoColor: {self.convert_color_name(auto_color)}")

    def convert_color_name(self, color):
        color_map = {
            RED: "Red",
            GREEN: "Green",
            BLUE: "Blue",
            YELLOW: "Yellow",
            PURPLE: "Purple",
        }
        return color_map.get(color, str(color))

    def on_mode_change(self, event):
        selection = self.dropdown.GetStringSelection()
        self.controller.change_mode(selection)
