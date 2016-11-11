### Author: Paul Brook
### Description:
### Category: Games
### License: GPLv3
### reboot-before-run: true

import raster
import chuckie.render
import chuckie
import chuckie.run
import chuckie.g as g

import ugfx
import buttons
import time

keymap = {
    "JOY_UP": chuckie.BUTTON_UP,
    "JOY_DOWN": chuckie.BUTTON_DOWN,
    "JOY_LEFT": chuckie.BUTTON_LEFT,
    "JOY_RIGHT": chuckie.BUTTON_RIGHT,
    "BTN_A": chuckie.BUTTON_JUMP,
    "BTN_B": chuckie.BUTTON_JUMP,
}

class TildaUI():
    def __init__(self):
        ugfx.init()
        if ugfx.backlight() == 0:
            ugfx.power_mode(ugfx.POWER_ON)
        ugfx.backlight(70)
        self.rm = chuckie.render.RenderManager()
        self.raster = raster.RasterTile()
        self._tick = time.ticks_ms()
        self._delta = 0
        buttons.init()

    def poll(self):
        g.buttons = 0
        for b, mask in keymap.items():
            if buttons.is_pressed(b):
                g.buttons |= mask

    def sound(self):
        pass

    def start_level(self):
        self.rm.start_level()

    def render(self):
        start = time.ticks_ms()
        self.rm.render()
        self.raster.raster()
        end = time.ticks_ms()
        self._delta += time.ticks_diff(self._tick, end) - 33
        print(self._delta, time.ticks_diff(self._tick, start), time.ticks_diff(start, end))
        self._tick = end
        if self._delta < 0:
            time.sleep_ms(-self._delta)

def main():
    ui = TildaUI()
    chuckie.run.run_game(ui)
