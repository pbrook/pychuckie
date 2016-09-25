from .constants import *
from . import g

def multiple_bits(mask):
    """Return True if more than one bit is set"""
    if mask == 0:
        return False
    return (mask & (mask - 1)) != 0


class DuckActor():
    def __init__(self, x, y):
        self.tilex = x
        self.tiley = y
        self.x = x << 3
        self.y = (y << 3) + 0x14
        self.mode = DUCK_BORED
        self.dir = DIR_R
        self.dirty = True

    def sprite(self):
        d = self.dir
        if self.mode == DUCK_BORED:
            if d == DIR_R:
                return 0
            elif d == DIR_L:
                return 2
            else:
                return 4
        elif self.mode == DUCK_STEP:
            if d == DIR_R:
                return 1
            elif d == DIR_L:
                return 3
            else:
                return 5
        elif self.mode in (DUCK_EAT2, DUCK_EAT4):
            if d == DIR_R:
                return 6
            else:
                return 8
        elif self.mode == DUCK_EAT3:
            if d == DIR_R:
                return 7
            else:
                return 9
        else:
            raise Exception("Bad duck mode")

    def move(self):
        self.dirty = True
        if self.mode == DUCK_BORED:
            # Figure out which way to go next
            x = self.tilex
            y = self.tiley
            newdir = 0
            if g.ls.check_tile(x - 1, y - 1, TILE_WALL):
                newdir |= DIR_L
            if g.ls.check_tile(x + 1, y - 1, TILE_WALL):
                newdir |= DIR_R
            if g.ls.check_tile(x, y - 1, TILE_LADDER):
                newdir |= DIR_DOWN
            if g.ls.check_tile(x, y + 2, TILE_LADDER):
                newdir |= DIR_UP
            if multiple_bits(newdir):
                # Avoid doing a u-turn if possible
                tmp = self.dir
                if (tmp & DIR_HORIZ) != 0:
                    tmp |= DIR_VERT
                else:
                    tmp |= DIR_HORIZ
                newdir &= tmp
            tmp = newdir
            while (newdir == 0) or multiple_bits(newdir):
                newdir = tmp & g.ls.duck_random()
            self.dir = newdir

            # Check for grain to eat.
            tmp = self.dir
            if (tmp & DIR_HORIZ) != 0:
                if tmp == DIR_L:
                    x -= 1
                else:
                    x += 1
                if g.ls.check_tile(x, y, TILE_GRAIN):
                    self.mode = DUCK_EAT1
        if self.mode == DUCK_EAT2:
            # Eat grain
            x = self.tilex - 1
            y = self.tiley
            if self.dir == DIR_R:
                x += 2
            if g.ls.check_tile(x, y, TILE_GRAIN):
                n = g.ls.read_tile(x, y) >> 4
                g.player_data.grain[n] = True
                g.ls.clear_tile(x, y)
        if self.mode >= DUCK_EAT1:
            # Eating
            if self.mode == DUCK_EAT4:
                self.mode = DUCK_BORED
            else:
                self.mode += 1
            return
        # Walking
        if self.mode == DUCK_STEP:
            self.mode = DUCK_BORED
            flag = 1
        else:
            self.mode = DUCK_STEP
            flag = 0

        if self.dir == DIR_L:
            self.x -= 4
            self.tilex -= flag
        elif self.dir == DIR_R:
            self.x += 4
            self.tilex += flag
        elif self.dir == DIR_UP:
            self.y += 4
            self.tiley += flag
        elif self.dir == DIR_DOWN:
            self.y -= 4
            self.tiley -= flag
        else:
            raise Exception("Bad duck direction")


