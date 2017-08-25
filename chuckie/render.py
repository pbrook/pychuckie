from . import sprites as sprite
from . import g
from .constants import *

dirty = True

g.moblist = []

class MOB():
    def __init__(self):
        g.moblist.append(self)
        self.sprite = None

    def _touch(self):
        tilex = self.x >> 3
        tiley = self.y >> 3
        partial_x = self.x & 7
        partial_y = self.y & 7
        w = (self.sprite.w + 7 + partial_x) >> 3
        h = (self.sprite.h + 7 + 7 - partial_y) >> 3
        if tilex + w > 20:
            w = 20 - tilex
        for j in range(tiley, tiley - h, -1):
            if (j < 0) or (j >= 26):
                continue
            offset = tilex + j * 20
            for i in range(w):
                g.dirty_tile[offset + i] = True

    def update(self, sprite, x, y):
        if self.sprite is not None:
            if self.x == x and self.y == y and self.sprite == sprite:
                return
            self._touch()
        self.sprite = sprite
        self.x = x
        self.y = y
        self._touch()

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
        self._player_mob.update(ps[n], p.x, p.y)

    def start_level(self):
        for n in range(len(g.dirty_tile)):
            g.dirty_tile[n] = True

        g.moblist.clear()
        for duck in g.ls.ducks:
            duck.mob = MOB()
            duck.update()
        bd = g.ls.big_duck
        bd.mob = MOB()
        self._cage_mob = MOB()
        if bd.active:
            s = sprite.cage_open
        else:
            s = sprite.cage_closed
        self._cage_mob.update(s, 0, 0xdc)
        s.render(0, 0xdc)
        self._player_mob = MOB()
        self._lift_mob = [MOB(), MOB()]

    def render(self, full=False):
        global dirty

        dirty = (dirty or full)
        if dirty:
            self.background()
        self.hud()
        self.score.draw(g.player_data.score)
        self.bonus.draw(g.player_data.bonus)
        self.ticks.draw(g.ls.timer_ticks)
        self.player()
        x = g.ls.lift_x
        if x is not None:
            for n in range(2):
                self._lift_mob[n].update(sprite.lift, x, g.ls.lift_y[n])
        dirty = False
