"""OpenGL setup and rendering code.
Copyright (C) 2016 Paul Brook
This code is licenced under the GNU GPL v3
"""
import numpy as np

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import chuckie
from chuckie import sprite_base
from chuckie import g

vertex_code = """
attribute vec2 position;
attribute vec2 vert_tex;
uniform vec2 offset;
varying vec2 frag_tex;
void main()
{
    vec2 pixel_pos;
    vec2 screen_pos;
    frag_tex = vert_tex;
    pixel_pos = position + offset;
    screen_pos = pixel_pos * vec2(2.0/160.0, 2.0/240.0) - vec2(1.0, 1.0);
    gl_Position = vec4(screen_pos, 0.0, 1.0);
}
"""

fragment_code = """
varying vec2 frag_tex;
uniform sampler2D tex;
uniform vec3 color;
void main()
{
    float alpha = texture2D(tex, frag_tex)[0];
    gl_FragColor = vec4(color, alpha);
}
"""

all_sprites = []

class GLSprite(sprite_base.BaseSprite):
    def __init__(self, *args):
        super().__init__(*args)
        all_sprites.append(self)

    def load(self, c):
        if c._x + self.w > c.TEX_SIZE:
            c._y += c._h
            c._x = 0
            c._h = 0
        if self.h > c._h:
            c._h = self.h
        if c._y + c._h > c.TEX_SIZE:
            raise Exception("Sprite texture too big")
        stride = c.TEX_SIZE - self.w
        dest = c._x + c._y * c.TEX_SIZE
        src = iter(self.data)
        for j in range(self.h):
            for i in range(self.w):
                if (i & 7) == 0:
                    mask = next(src)
                if (mask & 0x80) != 0:
                    alpha = 0xff
                else:
                    alpha = 0
                c._data[dest] = alpha
                dest += 1
                mask <<= 1
            dest += stride
        x1 = c._x / c.TEX_SIZE
        x2 = (c._x + self.w) / c.TEX_SIZE
        y1 = c._y / c.TEX_SIZE
        y2 = (c._y + self.h) / c.TEX_SIZE
        c._x += self.w
        self.index = len(c._vertex) // 4
        c._vertex.extend([0.0, 0.0, x1, y1])
        c._vertex.extend([0.0, -self.h, x1, y2])
        c._vertex.extend([self.w, -self.h, x2, y2])
        c._vertex.extend([self.w, 0.0, x2, y1])
        self._context = c
        color = self.color
        self._gl_color = (color.r / 255, color.g / 255, color.b / 255)

    def render(self, x, y):
        c = self._context
        glUniform2f(c._param_offset, x, y);
        glUniform3fv(c._param_color, 1, self._gl_color)
        glDrawArrays(GL_TRIANGLE_FAN, self.index, 4)

sprite_base.Sprite = GLSprite

class Renderer():
    TEX_SIZE = 128

    def __init__(self):
        self._x = 0
        self._y = 0
        self._h = 0
        self._data = bytearray(self.TEX_SIZE * self.TEX_SIZE)
        self._vertex = []

    def _setup_shaders(self):
        vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
        fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vertex, fragment)
        self._shader = program
        self._attr_position = glGetAttribLocation(program, "position")
        self._attr_tex = glGetAttribLocation(program, "vert_tex")
        self._param_color = glGetUniformLocation(program, "color")
        self._param_offset = glGetUniformLocation(program, "offset")
        self._param_tex = glGetUniformLocation(program, "tex")

    def finalize(self):
        for sprite in all_sprites:
            sprite.load(self)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable(GL_BLEND);
        glClearColor(0, 0, 0, 0);
        self._setup_shaders()
        glUseProgram(self._shader)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, self.TEX_SIZE, self.TEX_SIZE,
                     0, GL_RED, GL_UNSIGNED_BYTE, self._data)
        glUniform1i(self._param_tex, 0);

        self._vbo = vbo.VBO(np.array(self._vertex, dtype=np.float32))
        self._vbo.bind()
        glEnableVertexAttribArray(self._attr_position);
        glVertexAttribPointer(self._attr_position, 2, GL_FLOAT, GL_FALSE,
                              4 * 4, self._vbo);
        glEnableVertexAttribArray(self._attr_tex);
        glVertexAttribPointer(self._attr_tex, 2, GL_FLOAT, GL_FALSE,
                              4 * 4, self._vbo + (2 * 4));

    def render(self, draw):
        glClear(GL_COLOR_BUFFER_BIT)
        for tilex in range(20):
            for tiley in range(26):
                y = (tiley << 3) | 7
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
                    continue
                s.render(tilex << 3, y)

        for mob in g.moblist:
            if mob.sprite is None:
                continue
            mob.sprite.render(mob.x, mob.y)
        draw()

import chuckie.sprites as sprites
