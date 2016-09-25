"""2D raster drawing
Copyright (C) 2016 Paul Brook
This code is licenced under the GNU GPL v3
"""

from chuckie import sprite_base

import ugfx

def put_pixel(x, y, color):
    ugfx.line(2 * x, 239 - y, 2 * x + 1, 239 - y, color)

def raster_byte(x, y, mask, color):
    if mask == 0:
        return
    for i in range(8):
        if mask & 0x80:
            put_pixel(x + i, y, color)
        mask <<= 1

class RasterSprite(sprite_base.BaseSprite):
    def __init__(self, w, h, color, data):
        # Convert color to 565 format
        color = ugfx.html_color((color.r << 16) | (color.g << 8) | color.b)
        super().__init__(w, h, color, data)

    def render(self, x, y):
        data = iter(self.data)
        for j in range(self.h):
            for i in range(0, self.w, 8):
                raster_byte(x + i, y - j, next(data), self.color)

sprite_base.Sprite = RasterSprite
