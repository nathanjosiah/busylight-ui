import wx
from busylight.lights.kuando.busylight_omega import Busylight_Omega
from model import *
from controller import *
from view import *

if __name__ == "__main__":
    app = wx.App(False)
    light = Busylight_Omega.first_light()
    model = Model(light)
    controller = Controller(model)
    view = View(controller)
    controller.view = view

    controller.run_background_tasks()
    app.MainLoop()
