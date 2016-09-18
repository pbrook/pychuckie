import sprite
import chuckie
import logging

log = logging.getLogger(__name__)


class RenderManager():
    def digit(self, x, y, n):
        sprite.digit[n].render(x, y)

    def number(self, x, y, digits, n):
        while digits > 0:
            digits -= 1
            self.digit(x + digits * 5, y, n % 10)
            n //= 10

    def hud(self):
        x = 0 * 0x22 + 0x1b
        self.number(x + 1, 0xef, 6, chuckie.player_data.score)

        lives = chuckie.player_data.lives
        if lives > 8:
            lives = 8
        for n in range(lives):
            sprite.hat.render(x + n * 4, 0xe7)

    def background(self):
        sprite.score.render(0, 0xf0)
        # x + player * 0x22
        sprite.blank.render(0x1b, 0xf0)
        y = 0xe3
        sprite.player.render(0, y + 1)
        # digit current_player+1
        self.digit(0x1b, y, 1)
        sprite.level.render(0x24, y + 1)
        n = chuckie.player_data.level + 1
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
                t = chuckie.ls.read_tile(x, y)
                if (t & chuckie.TILE_LADDER) != 0:
                    s = sprite.ladder
                elif (t & chuckie.TILE_WALL) != 0:
                    s = sprite.wall
                elif (t & chuckie.TILE_EGG) != 0:
                    s = sprite.egg
                elif (t & chuckie.TILE_GRAIN) != 0:
                    s = sprite.grain
                else:
                    s = None
                if s is not None:
                    s.render(x << 3, (y << 3) | 7)
        if chuckie.ls.big_duck.active:
            s = sprite.cage_open
        else:
            s = sprite.cage_closed
        s.render(0, 0xdc)

    def ducks(self):
        for duck in chuckie.ls.ducks:
            n = duck.sprite()
            x = duck.x
            if n >= 8:
                x -= 8
            sprite.duck[n].render(x, duck.y)

    def player(self):
        p = chuckie.player
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
        if p.mode != chuckie.PLAYER_CLIMB:
            if p.move_x == 0:
                n = 0
        else:
            if p.move_y == 0:
                n = 0
        ps[n].render(p.x, p.y)

    def render(self):
        self.background()
        self.hud()
        y = 0xe3
        self.number(0x66, y, 3, chuckie.player_data.bonus)
        self.number(0x91, y, 3, chuckie.ls.timer_ticks)
        self.ducks()
        self.player()
        x = chuckie.ls.lift_x
        if x is not None:
            for y in chuckie.ls.lift_y:
                sprite.lift.render(x, y)
        bd = chuckie.ls.big_duck
        if bd.dir != 0:
            s = sprite.bigduck_l
        else:
            s = sprite.bigduck_r
        s[bd.frame].render(bd.x, bd.y)
