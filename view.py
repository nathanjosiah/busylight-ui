import wx
from constants import *

class View(wx.Frame):
    color_map = {
        RED: "Red",
        GREEN: "Green",
        BLUE: "Blue",
        YELLOW: "Yellow",
        PURPLE: "Purple",
    }

    def __init__(self, controller):
        super().__init__(None, title="Busy Light Control Panel", size=(300, 200))
        self.controller = controller

        # Panel and layout
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.mode_label = wx.StaticText(panel, label="", size=(300, 25))
        vbox.Add(self.mode_label, flag=wx.EXPAND | wx.ALL, border=10)

        # Active color label and swatch
        self.color_label = wx.StaticText(panel, label="", size=(100, 25))
        self.color_swatch = wx.Panel(panel, size=(15, 15))
        color_row = wx.BoxSizer(wx.HORIZONTAL)
        color_row.Add(self.color_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        color_row.Add(self.color_swatch, 0, wx.ALL, 5)
        vbox.Add(color_row, 0, wx.EXPAND)

        self.auto_color_label = wx.StaticText(panel, label="", size=(300, 25))
        vbox.Add(self.auto_color_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.dropdown = wx.Choice(panel, choices=[AUTOMATIC, OFF] + list(self.color_map.values()))
        vbox.Add(self.dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        self.dropdown.Bind(wx.EVT_CHOICE, self.on_mode_change)
        self.dropdown.Bind(wx.EVT_WINDOW_DESTROY, self.on_window_destroy)
        panel.SetSizer(vbox)
        self.Show()
        self.SetFocus()

    def update_labels(self, mode, color, auto_color):
        self.mode_label.SetLabel(f"Mode: {mode}")
        self.color_label.SetLabel(f"Color: {self.convert_color_name(color)}")
        self.color_swatch.SetBackgroundColour(color)
        self.auto_color_label.SetLabel(f"AutoColor: {self.convert_color_name(auto_color)}")
        self.Refresh()

    def convert_color_name(self, color):
        return self.color_map.get(color, str(color))

    def on_mode_change(self, event):
        selection = self.dropdown.GetStringSelection()
        self.controller.change_mode(selection)

    def on_window_destroy(self, event):
        self.controller.handle_window_destroy()
