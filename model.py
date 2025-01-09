from constants import *

class Model:
    def __init__(self, light):
        self.light = light
        self.color = GREEN # Default green
        self.auto_color = GREEN
        self.override = None
        self.mode = AUTOMATIC

    def get_color(self):
        return self.color

    def get_auto_color(self):
        return self.auto_color

    def get_mode(self):
        return self.mode

    def set_automatic_color(self, new_color):
        self.auto_color = new_color
        if self.mode == AUTOMATIC:
            self.set_color(new_color)

    def set_color(self, new_color):
        if new_color == OFF:
            self.light.off()
        else:
            self.light.on(new_color)
        self.color = new_color

    def set_mode(self, new_mode):
        self.mode = new_mode
        if new_mode == OFF:
            self.light.off()
        elif new_mode == AUTOMATIC:
            self.color = self.auto_color
            self.override = None
            self.set_color(self.color)
        else:
            self.override = self.get_color_from_mode(new_mode)
            self.set_color(self.override)

    def get_color_from_mode(self, mode):
        color_map = {
            "Red": RED,
            "Green": GREEN,
            "Blue": BLUE,
            "Yellow": YELLOW,
            "Purple": PURPLE,
        }
        return color_map.get(mode, (0, 0, 0))

    def refresh(self):
        if self.mode == AUTOMATIC:
            self.set_color(self.auto_color)
        elif self.mode != OFF:
            self.set_color(self.override)

