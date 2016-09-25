from . import sprites as sprite
from . import g
from .constants import *

dirty = True

class RenderNumber():
    def __init__(self, x, y, n):
        self._x = x
        self._y = y
        self._old = [10] * n
        self._oldval = None

    def draw(self, val):
        if val == self._oldval and not dirty:
            return
        digit = len(self._old)
        while digit > 0:
            digit -= 1
            newval = val % 10
            if dirty or newval != self._old[digit]:
                self._old[digit] = newval
                x = self._x + digit * 5
                y = self._y
                sprite.nodigit.render(x, y)
                sprite.digit[newval].render(x, y)
            val //= 10


class RenderManager():
    def __init__(self):
        self.bonus = RenderNumber(0x66, 0xe3, 3)
        self.ticks = RenderNumber(0x91, 0xe3, 3)
        x = 0 * 0x22 + 0x1b
        self.score = RenderNumber(x, 0xef, 6)
        self.lives = 0

    def digit(self, x, y, n):
        sprite.digit[n].render(x, y)

    def number(self, x, y, digits, n):
        while digits > 0:
            digits -= 1
            self.digit(x + digits * 5, y, n % 10)
            n //= 10

    def hud(self):
        self.score.draw(g.player_data.score)

        x = 0 * 0x22 + 0x1b
        lives = g.player_data.lives
        if lives > 8:
            lives = 8
        if dirty or self.lives != lives:
            self.lives = lives
            for n in range(8):
                if n < lives:
                    s = sprite.hat
                else:
                    s = sprite.blackhat
                s.render(x + n * 4, 0xe7)

    def background(self):
        sprite.score.render(0, 0xf0)
        # x + player * 0x22
        sprite.blank.render(0x1b, 0xf0)
        y = 0xe3
        sprite.player.render(0, y + 1)
        # digit current_player+1
        self.digit(0x1b, y, 1)
        sprite.level.render(0x24, y + 1)
        n = g.player_data.level + 1
        self.digit(0x45, y, n % 10)
        n //= 10
        self.digit(0x40, y, n % 10)
        if n >= 10:
            self.digit(0x3b, y, n // 10)

        sprite.bonus.render(0x4e, y + 1)
        self.digit(0x75, y, 0)
        sprite.time.render(0x7e, y + 1)

        for x in range(20):
            for y in range(25):
                t = g.ls.read_tile(x, y)
                if (t & TILE_LADDER) != 0:
                    s = sprite.ladder
                elif (t & TILE_WALL) != 0:
                    s = sprite.wall
                elif (t & TILE_EGG) != 0:
                    s = sprite.egg
                elif (t & TILE_GRAIN) != 0:
                    s = sprite.grain
                else:
                    s = None
                if s is not None:
                    s.render(x << 3, (y << 3) | 7)
        if g.ls.big_duck.active:
            s = sprite.cage_open
        else:
            s = sprite.cage_closed
        s.render(0, 0xdc)

    def ducks(self):
        for duck in g.ls.ducks:
            if not (dirty or duck.dirty):
                continue
            n = duck.sprite()
            x = duck.x
            if n >= 8:
                x -= 8
            sprite.duck[n].render(x, duck.y)
            duck.dirty = False

    def player(self):
        p = g.player
        face = p.face
        if face == 0:
            ps = sprite.player_up
            n = (p.y >> 1) & 3
        else:
            if face < 0:
                ps = sprite.player_l
            else:
                ps = sprite.player_r
            n = (p.x >> 1) & 3
        if p.mode != PLAYER_CLIMB:
            if p.move_x == 0:
                n = 0
        else:
            if p.move_y == 0:
                n = 0
        ps[n].render(p.x, p.y)

    def render(self):
        global dirty

        if dirty:
            self.background()
        self.hud()
        self.bonus.draw(g.player_data.bonus)
        self.ticks.draw(g.ls.timer_ticks)
        self.ducks()
        self.player()
        x = g.ls.lift_x
        if x is not None:
            for y in g.ls.lift_y:
                sprite.lift.render(x, y)
        bd = g.ls.big_duck
        if dirty or bd.dirty:
            if bd.dir != 0:
                s = sprite.bigduck_l
            else:
                s = sprite.bigduck_r
            s[bd.frame].render(bd.x, bd.y)
            bd.dirty = False
        dirty = False
