#! /usr/bin/env python3

import pygame
import pygame.locals as pgl
import glrender
import chuckie.render
import chuckie
import chuckie.g as g
import logging
import time
import sys

keymap = {
    pgl.K_UP: chuckie.BUTTON_UP,
    pgl.K_DOWN: chuckie.BUTTON_DOWN,
    pgl.K_LEFT: chuckie.BUTTON_LEFT,
    pgl.K_RIGHT: chuckie.BUTTON_RIGHT,
    pgl.K_SPACE: chuckie.BUTTON_JUMP,
}

class SDLUI():
    def __init__(self):
        width = 640
        height = 480
        pygame.init()
        video_flags = pgl.OPENGL | pgl.DOUBLEBUF
        pygame.display.set_mode((width, height), video_flags)

        self.glr = glrender.Renderer()
        self.glr.finalize()
        self.rm = chuckie.render.RenderManager()
        self.next_tick = time.monotonic()

    def poll(self):
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                sys.exit(0)
            elif event.type == pgl.KEYDOWN:
                g.buttons |= keymap.get(event.key, 0)
            elif event.type == pgl.KEYUP:
                if event.key == pgl.K_ESCAPE:
                    sys.exit(0)
                elif event.key == ord('l'):
                    chuckie.cheat = True
                else:
                    g.buttons &= ~keymap.get(event.key, 0)

    def sound(self):
        pass

    def render(self):
        delta = self.next_tick - time.monotonic()
        if delta < -1:
            self.next_tick = time.monotonic()
        else:
            if delta > 0:
                time.sleep(delta)
            self.next_tick += 1.0 / 30
        self.glr.render(self.rm.render)
        pygame.display.flip()

def main():
    logging.basicConfig(level=logging.DEBUG)
    ui = SDLUI()
    chuckie.run_game(ui);

if __name__ == "__main__":
    main()
