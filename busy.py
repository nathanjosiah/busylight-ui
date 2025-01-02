import datetime
import threading
from busylight.lights.kuando.busylight_omega import Busylight_Omega
import asyncio
import wx

light = Busylight_Omega.first_light()

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
purple = (255, 0, 255)
mode = "Automatic"
frame = None

def convert_color_name(tuple_str):
    match str(tuple_str):
        case "(255, 0, 0)": return "red"
        case "(0, 255, 0)": return "green"
        case "(0, 0, 255)": return "blue"
        case "(255, 255, 0)": return "yellow"
        case "(255, 0, 255)": return "purple"
    return str(tuple_str)

def set_mode_label(text):
    global frame
    if frame is None:
        return
    frame.mode_label.SetLabel("Mode: " + convert_color_name(text))

def set_autocolor_label(text):
    global frame
    if frame is None:
        return
    frame.autocolor_label.SetLabel("Autocolor:" + convert_color_name(text))

def set_color_label(text):
    global frame
    if frame is None:
        return
    frame.color_label.SetLabel("Color: " + convert_color_name(text))

class ColorSingleton:
    color = green
    auto_color = green
    override = None

    def get_color(self):
        return self.color

    def get_autocolor(self):
        return self.auto_color

    def get_mode(self):
        global mode
        return mode

    def set_automatic_color(self, new_color):
        global mode
        set_autocolor_label(str(new_color))
        print("Auto color set to", new_color)
        self.auto_color = new_color
        if mode == "Automatic":
            self.set_color(new_color)

    def set_color(self, new_color):
        set_color_label(str(new_color))
        if new_color == "Off":
            light.off()
        else:
            light.on(new_color)
        self.color = new_color

    def refresh(self):
        global mode
        if mode == "Automatic":
            color.set_color(color.get_color())
            return
        if mode == "Off":
            return

        self.set_color(self.override)

    def set_mode(self, new_mode):
        global mode
        mode = new_mode
        set_mode_label(new_mode)
        if mode == "Off":
            light.off()
            return
        if mode == "Automatic":
            self.color = self.auto_color
            self.override = None
            self.set_color(self.get_color())
            return

        if mode == "Red":
            self.override = red
        elif mode == "Green":
            self.override = green
        elif mode == "Blue":
            self.override = blue
        elif mode == "Yellow":
            self.override = yellow
        elif mode == "Purple":
            self.override = purple

        color.refresh()

color = ColorSingleton()


async def monitor_logs():
    process = await asyncio.create_subprocess_exec(
        "log", "stream", "--predicate", 'eventMessage contains "MSTeams"', "--info",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    is_active = False

    async for line in process.stdout:
        line = line.decode("utf-8").strip()
        if "Active = YES" in line:
            if not is_active:
                print("Teams is active")
                is_active = True
                color.set_automatic_color(red)
        elif "Active = NO" in line:
            if is_active:
                print("Teams is inactive")
                is_active = False
                color.set_automatic_color(green)


async def automatic_refresh_light():
    global color
    while True:
        t = datetime.datetime.now()
        print("Hour is", t.hour)
        if t.weekday() == 5 or t.weekday() == 6:
            print("sleeping for 7 hours")
            color.set_automatic_color("Off")
            await asyncio.sleep(60 * 60 * 7)
            continue
        if t.hour > 18 or t.hour < 7:
            print("sleeping for 30 minutes")
            color.set_automatic_color("Off")
            await asyncio.sleep(60 * 30)
            continue
        color.refresh()
        await asyncio.sleep(25)

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Busy Light Control Panel", size=(300, 200))

        # Panel and layout
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.mode_label = wx.StaticText(panel, label="Mode: " + convert_color_name(mode), size=(300, 25))
        vbox.Add(self.mode_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.color_label = wx.StaticText(panel, label="Color: " + convert_color_name(color.get_color()), size=(300, 25))
        vbox.Add(self.color_label, flag=wx.EXPAND | wx.ALL, border=10)

        self.autocolor_label = wx.StaticText(panel, label="AutoColor: " + convert_color_name(color.get_autocolor()), size=(300, 25))
        vbox.Add(self.autocolor_label, flag=wx.EXPAND | wx.ALL, border=10)

        # Dropdown (Choice)
        self.dropdown = wx.Choice(panel, choices=["Automatic", "Off", "Red", "Green", "Blue", "Yellow", "Purple"])
        vbox.Add(self.dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Bind event to update the status when selection changes
        self.dropdown.Bind(wx.EVT_CHOICE, self.on_select)

        panel.SetSizer(vbox)
        self.Show()

    def on_select(self, event):
        global color
        selection = self.dropdown.GetStringSelection()
        color.set_mode(selection)

def run_monitor_logs_in_threads():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_logs())

def run_refresh_in_threads():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(automatic_refresh_light())
def run_background_threads():
    thread1 = threading.Thread(target=run_monitor_logs_in_threads)
    thread2 = threading.Thread(target=run_refresh_in_threads)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

async def main():
    global frame
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()

try:
    threading.Thread(target=run_background_threads).start()
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopping...")
    light.off()






