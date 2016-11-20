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
black = ugfx.html_color(0)

@micropython.asm_thumb
def raster1(r0, r1): #mask, color
    movwt(r7, 0x60800000)
    mov(r4, 0x80) # test
    label(again)
    tst(r0, r4)
    beq(isblack)
    mov(r5, 8)
    mov(r6, r1)
    lsr(r6, r5)
    strb(r6, [r7, 0])
    strb(r1, [r7, 0])
    strb(r6, [r7, 0])
    strb(r1, [r7, 0])
    b(done)
    label(isblack)
    mov(r6, 0)
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    label(done)
    mov(r5, 1)
    lsr(r4, r5)
    bne(again)

@micropython.asm_thumb
def raster2(r0, r1, r2, r3): # tile_mask, tile_color, mob_mask, mob_color
    movwt(r7, 0x60800000)
    mov(r4, 0x80) # test
    label(again)
    tst(r2, r4)
    beq(tile)
    mov(r5, 8)
    mov(r6, r3)
    lsr(r6, r5)
    strb(r6, [r7, 0])
    strb(r3, [r7, 0])
    strb(r6, [r7, 0])
    strb(r3, [r7, 0])
    b(done)
    label(tile)
    tst(r0, r4)
    beq(isblack)
    mov(r5, 8)
    mov(r6, r1)
    lsr(r6, r5)
    strb(r6, [r7, 0])
    strb(r1, [r7, 0])
    strb(r6, [r7, 0])
    strb(r1, [r7, 0])
    b(done)
    label(isblack)
    mov(r6, 0)
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    strb(r6, [r7, 0])
    label(done)
    mov(r5, 1)
    lsr(r4, r5)
    bne(again)

@micropython.asm_thumb
def stream(r0, r1): #addr, color
    mov(r2, r1)
    mov(r3, 8)
    lsr(r2, r3)
    strb(r2, [r0, 0])
    strb(r1, [r0, 0])
    strb(r2, [r0, 0])
    strb(r1, [r0, 0])

class RasterTile():
    def raster_mobs(self, moblist):
        mask = 0
        color = 0
        for mob in moblist:
            dy = mob.y - self.y
            if dy < 0:
                continue
            sprite = mob.sprite
            if dy >= sprite.h:
                continue

            dx = mob.x - self.x
            color = sprite.color
            w = sprite.w >> 3
            offset = dy * w
            if w == 1 or dx >= 0:
                data = sprite.data[offset]
                if dx < 0:
                    data = (data << -dx) & 0xff
                else:
                    data >>= dx
            else:
                while dx < -7:
                    dx += 8
                    offset += 1
                    w -= 1
                data = sprite.data[offset]
                if dx != 0:
                    data = (data << -dx) & 0xff
                    if w > 1:
                        data |= sprite.data[offset + 1] >> (8 + dx)

            mask |= data
        return (mask, color)
        
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

    def raster_notile(self, mobs):
        for j in range(8):
            ugfx.stream_start(2 * self.x, 239 - self.y, 16, 1)
            (mob_mask, mob_color) = self.raster_mobs(mobs)

            raster1(mob_mask, mob_color)
            #mask = 0x80
            #while mask != 0:
            #    if mob_mask & mask:
            #        color = mob_color
            #    else:
            #        color = black
            #    ugfx.stream_color(color)
            #    ugfx.stream_color(color)
            #    mask >>= 1

            self.y -= 1
            ugfx.stream_stop()

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
            self.raster_notile(mobs)
            return

        for j in range(8):
            ugfx.stream_start(2 * self.x, 239 - self.y, 16, 1)
            tile_color = s.color
            tile_mask = s.data[j]
            (mob_mask, mob_color) = self.raster_mobs(mobs)

            raster2(tile_mask, tile_color, mob_mask, mob_color)
            #mask = 0x80
            #while mask != 0:
            #    if mob_mask & mask:
            #        color = mob_color
            #    elif tile_mask & mask:
            #        color = tile_color
            #    else:
            #        color = black
            #    ugfx.stream_color(color)
            #    ugfx.stream_color(color)
            #    mask >>= 1

            self.y -= 1
            ugfx.stream_stop()


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
