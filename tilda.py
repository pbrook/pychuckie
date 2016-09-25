import raster
import chuckie.render
import chuckie
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

class Wibble():
    def __init__(self):
        ugfx.init()
        if ugfx.backlight() == 0:
            ugfx.power_mode(ugfx.POWER_ON)
        ugfx.backlight(70)
        self.rm = chuckie.render.RenderManager()
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

    def render(self):
        start = time.ticks_ms()
        if chuckie.render.dirty:
            ugfx.area(0, 0, 320, 240, ugfx.BLACK)
        self.rm.render()
        end = time.ticks_ms()
        self._delta += time.ticks_diff(self._tick, end) - 33
        print(self._delta, time.ticks_diff(self._tick, start), time.ticks_diff(self._tick, end))
        self._tick = end
        if self._delta < 0:
            time.sleep_ms(-self._delta)

def main():
    ui = Wibble()
    chuckie.run_game(ui)
