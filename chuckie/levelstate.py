from .bigduck import BigDuck
from .duck import DuckActor
from .leveldata import leveldata
from .constants import *
from . import g

class LevelState():
    def __init__(self, current_level):
        self.big_duck = BigDuck(current_level > 7)

        self.duck_timer = 0
        self.current_duck = 0
        if current_level < 32:
            self.duck_speed = 8
        else:
            self.duck_speed = 5
        self.is_dead = False
        self.bonus_hold = 0
        self.rand_high = 0x767676
        self.rand_low = 0x76

        epoch = current_level // 8
        if epoch > 8:
            epoch = 8

        self.timer_ticks = 900 - (epoch * 100)

        level = leveldata[current_level % 8]
        self.num_ducks = len(level['duck'])
        self.levelmap = [0] * (20 * 25)

        for x1, y, x2 in level['wall']:
            for x in range(x1, x2 + 1):
                self.set_tile(x, y, TILE_WALL)

        for x, y1, y2 in level['ladder']:
            for y in range(y1, y2 + 1):
                self.set_tile(x, y, TILE_LADDER)

        self.lift_x = level.get('lift')
        if self.lift_x is not None:
            self.lift_x <<= 3
            self.current_lift = 0
            self.lift_y = [8, 0x5a]

        self.eggs_left = 0
        for i, (x, y) in enumerate(level['egg']):
            if not g.player_data.egg[i]:
                self.set_tile(x, y, (i << 4) | TILE_EGG)
                self.eggs_left += 1

        for i, (x, y) in enumerate(level['grain']):
            if not g.player_data.grain[i]:
                self.set_tile(x, y, (i << 4) | TILE_GRAIN)

        if epoch == 1:
            num_ducks = 0
        elif epoch >= 3:
            num_ducks = 5
        else:
            num_ducks = level['num_ducks']

        self.ducks = [DuckActor(x, y)
                      for x, y in level['duck'][:num_ducks]]

    def move_lift(self):
        if self.lift_x is None:
            return
        y = self.lift_y[self.current_lift]
        y += 2
        if y == 0xe0:
            y = 6
        self.lift_y[self.current_lift] = y
        self.current_lift = 1 - self.current_lift

    def duck_random(self):
        carry = (((self.rand_low & 0x48) + 0x38) & 0x40) != 0
        self.rand_high = (self.rand_high << 1) & 0x1ffffff
        if carry:
            self.rand_high |= 1
        self.rand_low = ((self.rand_low << 1) & 0xff) | \
            ((self.rand_high >> 24) & 1)
        return self.rand_low

    def move_ducks(self):
        self.duck_timer += 1
        if self.duck_timer == 8:
            self.duck_timer = 0
            self.big_duck.move()
            return

        if self.duck_timer == 4:
            # Update bonus/timer
            if self.bonus_hold > 0:
                self.bonus_hold -= 1
                return

            self.timer_ticks -= 1
            if self.timer_ticks == 0:
                self.is_dead = True
                return
            tmp = self.timer_ticks % 5
            if tmp != 0:
                return
            if g.player_data.bonus > 0:
                g.player_data.bonus -= 10
            return

        if self.current_duck == 0:
            self.current_duck = self.duck_speed
        else:
            self.current_duck -= 1
        if self.current_duck >= len(self.ducks):
            return
        self.ducks[self.current_duck].move()

    def collision_detect(self):
        for duck in self.ducks:
            if (abs(duck.x - g.player.x) <= 5) and \
                    (abs(duck.y - 1 - g.player.y) <= 14):
                self.is_dead = True

        if self.big_duck.collision():
            self.is_dead = True

    def read_tile(self, x, y):
        # Movement code generates out of bounds reads
        if y >= 0x19 or x >= 0x14:
            return 0
        return self.levelmap[x + y * 20]

    def check_tile(self, x, y, which):
        """Return True if tile is of specified type"""
        # Movement code generates out of bounds reads
        if y >= 0x19 or x >= 0x14:
            return False
        return (self.levelmap[x + y * 20] & which) != 0

    def set_tile(self, x, y, val):
        n = x + y * 20
        self.levelmap[n] |= val
        g.dirty_tile[n] = True

    def clear_tile(self, x, y):
        n = x + y * 20
        self.levelmap[n] = 0
        g.dirty_tile[n] = True
