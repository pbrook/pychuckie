"""2D raster drawing
Copyright (C) 2016 Paul Brook
This code is licenced under the GNU GPL v3
"""

import chuckie
from chuckie import sprite_base
from chuckie import g

import ugfx
import array

def put_pixel(x, y, color):
    ugfx.line(2 * x, 239 - y, 2 * x + 1, 239 - y, color)


tile_buffer = array.array('h', [0]*8)

class RasterTile():
    def raster_sprite(self, sprite, dx, dy):
        color = sprite.color
        offset = (dy * sprite.w) >> 3
        x = -dx
        for i in range(sprite.w >> 3):
            mask = sprite.data[offset]
            for n in range(8):
                if (x >= 0) and (x < 8):
                    if mask & 0x80:
                        tile_buffer[x] = color
                mask <<= 1
                x += 1
            offset += 1
        
    def raster_mob(self, mob):
        dx = self.x - mob.x
        dy = mob.y - self.y
        if dy < 0:
            return
        if dy >= mob.sprite.h:
            return
        self.raster_sprite(mob.sprite, dx, dy)

    def _flush(self):
        x = self.x
        y = self.y
        ugfx.stream_start(2 * x, 239 - y, 16, 1)
        for n in range(8):
            color = tile_buffer[n]
            ugfx.stream_color(color)
            ugfx.stream_color(color)
        ugfx.stream_stop()

    def raster(self):
        n = 0
        for tilex in range(20):
            x = tilex << 3
            self.x = x
            mobs = None

            n = tilex
            for y in range(26):
                if g.dirty_tile[n]:
                    if mobs is None:
                        mobs = []
                        for mob in g.moblist:
                            if mob.sprite is None:
                                continue
                            dx = self.x - mob.x
                            if dx <= -8:
                                continue
                            if dx >= mob.sprite.w:
                                continue
                            mobs.append(mob)
                    self.raster_tile(tilex, y, mobs)
                    g.dirty_tile[n] = False
                n += 20

    def raster_tile(self, tilex, tiley, mobs):
        y = (tiley << 3) | 7
        self.y = y
        t = g.ls.read_tile(tilex, tiley)
        if (t & chuckie.TILE_LADDER) != 0:
            s = sprites.ladder
        elif (t & chuckie.TILE_WALL) != 0:
            s = sprites.wall
        elif (t & chuckie.TILE_EGG) != 0:
            s = sprites.egg
        elif (t & chuckie.TILE_GRAIN) != 0:
            s = sprites.grain
        else:
            s = None

        black = ugfx.html_color(0)
        for j in range(8):
            if s is None:
                mask = 0
                color = black
            else:
                color = s.color
                mask = s.data[j]
            for i in range(8):
                if mask & 0x80:
                    tile_buffer[i] = color
                else:
                    tile_buffer[i] = black
                mask <<= 1
            for mob in mobs:
                self.raster_mob(mob)
            self._flush()
            self.y -= 1


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

import chuckie.sprites as sprites
