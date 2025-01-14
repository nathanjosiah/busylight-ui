import threading
import asyncio
import datetime
import sys
from constants import *


class Controller:
    def __init__(self, model):
        self.threads = []
        self.model = model
        self.view = None  # Temporal coupling due to circular dependency
        self._stop_event = threading.Event()

    def change_mode(self, mode):
        self.model.set_mode(mode)
        self.update_view()

    def handle_window_destroy(self):
        print("Window closed. Initiating shut down...")
        self._stop_event.set()
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        sys.exit(0)

    def update_view(self):
        self.view.update_labels(self.model.get_mode(), self.model.get_color(), self.model.get_auto_color())

    async def monitor_logs(self):
        process = await asyncio.create_subprocess_exec(
            "log", "stream", "--predicate", 'eventMessage contains "MSTeams"', "--info",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        is_active = False

        async for line in process.stdout:
            if self._stop_event.is_set():
                process.terminate()  # Stop the subprocess if the app is closing
                break

            line = line.decode("utf-8").strip()
            if "Active = YES" in line:
                if not is_active:
                    is_active = True
                    self.model.set_automatic_color(RED)
                    self.update_view()
            elif "Active = NO" in line:
                if is_active:
                    is_active = False
                    self.model.set_automatic_color(GREEN)
                    self.update_view()

    async def automatic_refresh_light(self):
        while not self._stop_event.is_set():
            now = datetime.datetime.now()
            print("[Refresh]")
            print(f" - Sleep on day 5&6 and between hour 19 and 7")
            print(f" - Day is {now.weekday()} and hour is {now.hour}")
            if now.weekday() in [5, 6] or now.hour < 7 or now.hour > 18:
                print(f" - Sleeping")
                self.model.set_automatic_color(OFF)
            else:
                print(f" - Refreshing")
                self.model.refresh()
            self.update_view()
            print("[/Refresh] - Waiting 30 seconds")
            await asyncio.sleep(30)

    def run_background_tasks(self):
        self.threads.append(threading.Thread(target=self._run_async, args=(self.monitor_logs,)))
        self.threads.append(threading.Thread(target=self._run_async, args=(self.automatic_refresh_light,)))

        for thread in self.threads:
            thread.start()

    def _run_async(self, coro):
        asyncio.run(self._async_wrapper(coro))

    async def _async_wrapper(self, coro):
        try:
            await coro()
        except asyncio.CancelledError:
            pass
