"""OpenGL setup and rendering code.
Copyright (C) 2016 Paul Brook
This code is licenced under the GNU GPL v3
"""
import numpy as np

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

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

TEX_SIZE = 128

class GLSprite():
    def __init__(self, context, x, y, sprite, index):
        self.x1 = x / context.TEX_SIZE
        self.x2 = (x + sprite.w) / context.TEX_SIZE
        self.y1 = y / context.TEX_SIZE
        self.y2 = (y + sprite.h) / context.TEX_SIZE
        self.w = sprite.w
        self.h = sprite.h
        c = sprite.color
        self.color = (c.r / 255, c.g / 255, c.b / 255)
        self.index = index
        self._context = context

    def render(self, x, y):
        c = self._context
        glUniform2f(c._param_offset, x, y);
        glUniform3fv(c._param_color, 1, self.color)
        glDrawArrays(GL_TRIANGLE_FAN, self.index, 4)

class Renderer():
    TEX_SIZE = 128

    def __init__(self):
        self._x = 0
        self._y = 0
        self._h = 0
        self._data = bytearray(self.TEX_SIZE * self.TEX_SIZE)
        self._vertex = []
        self._vertex_count = 0

    def load(self, sprite):
        if self._x + sprite.w > self.TEX_SIZE:
            self._y += self._h
            self._x = 0
            self._h = 0
        if sprite.h > self._h:
            self._h = sprite.h
        if self._y + self._h > self.TEX_SIZE:
            raise Exception("Sprite texture too big")
        stride = self.TEX_SIZE - sprite.w
        dest = self._x + self._y * self.TEX_SIZE
        src = iter(sprite.data)
        for j in range(sprite.h):
            for i in range(sprite.w):
                if (i & 7) == 0:
                    mask = next(src)
                if (mask & 0x80) != 0:
                    alpha = 0xff
                else:
                    alpha = 0
                self._data[dest] = alpha
                dest += 1
                mask <<= 1
            dest += stride
        index = len(self._vertex)
        t = GLSprite(self, self._x, self._y, sprite, self._vertex_count)
        self._vertex.extend([0.0, 0.0, t.x1, t.y1])
        self._vertex.extend([0.0, -t.h, t.x1, t.y2])
        self._vertex.extend([t.w, -t.h, t.x2, t.y2])
        self._vertex.extend([t.w, 0.0, t.x2, t.y1])
        self._vertex_count += 4
        self._x += sprite.w
        return t.render

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
        draw()
