from .constants import *
from .import g

ls = None

def squidge(n):
    pass

class PlayerActor():
    def __init__(self):
        global ls
        ls = g.ls
        self.x = 0x3c
        self.y = 0x20
        # FIXME
        self.tilex = 7
        self.tiley = 2
        self.partial_x = 7
        self.partial_y = 0
        self.mode = PLAYER_WALK
        self.face = 1
        self.button_ack = 0x1f
        self.extra_life = False

        self.move_x = 0
        self.move_y = 0
        self.slide = 0
        self.fall = 0

    def blocked(self):
        tmp = self.move_x
        if tmp == 0:
            return False
        if tmp < 0:
            # Moving Left
            if self.x == 0:
                return True
            if self.partial_x >= 2:
                return False
            if self.move_y == 2:
                return False

            x = self.tilex - 1
            y = self.tiley
            tmp = self.partial_y + self.move_y
            if tmp < 0:
                y -= 1
            if tmp >= 8:
                y += 1

            if ls.read_tile(x, y) == TILE_WALL:
                return True
            if self.move_y >= 0:
                return False
            x = self.tilex - 1
            y += 1
            return ls.read_tile(x, y) == TILE_WALL
        # Moving Right
        tmp = self.x
        if tmp > 0x98:
            return True
        if self.partial_x < 5:
            return False
        if self.move_y == 2:
            return False
        x = self.tilex + 1
        y = self.tiley
        tmp = self.partial_y + self.move_y
        if tmp < 0:
            y -= 1
        elif tmp >= 8:
            y += 1
        if ls.read_tile(x, y) == 1:
            return True
        if self.move_y >= 0:
            return False
        x = self.tilex + 1
        y += 1
        return (ls.read_tile(x, y) == 1)

    def animate(self):
        self.x += self.move_x
        tmp = self.partial_x + self.move_x
        if tmp < 0:
            self.tilex -= 1
        if tmp >= 8:
            self.tilex += 1
        self.partial_x = tmp & 7

        self.y += self.move_y
        tmp = self.partial_y + self.move_y
        if tmp < 0:
            self.tiley -= 1
        if tmp >= 8:
            self.tiley += 1
        self.partial_y = tmp & 7
        x = self.tilex
        y = self.tiley
        if self.partial_y >= 4:
            y += 1
        if ls.check_tile(x, y, TILE_EGG):
            # Got egg
            ls.eggs_left -= 1
            squidge(6)
            n = ls.read_tile(x, y) >> 4
            g.player_data.egg[n] = True
            ls.clear_tile(x, y)
            tmp = min((g.player_data.level >> 2) + 1, 10)
            g.player_data.add_score(tmp * 100)
        elif ls.check_tile(x, y, TILE_GRAIN):
            # Got grain
            squidge(5)
            n = ls.read_tile(x, y) >> 4
            g.player_data.grain[n] = True
            ls.clear_tile(x, y)
            g.player_data.add_score(50)
            ls.bonus_hold = 14

    def grab_ladder(self, want_move):
        tmp = self.partial_x + self.move_x
        if tmp != 3:
            return
        if want_move == 0:
            return
        if want_move > 0:
            x = self.tilex
            y = self.tiley + 1
            if not ls.check_tile(x, y, TILE_LADDER):
                if self.partial_y >= 4:
                    y += 1
                if not ls.check_tile(x, y, TILE_LADDER):
                    return
            self.mode = PLAYER_CLIMB
            tmp = self.partial_y + self.move_y
            if tmp & 1:
                self.move_y += 1
            return

        x = self.tilex
        y = self.tiley
        if not ls.check_tile(x, y, TILE_LADDER):
            return
        x = self.tilex
        y = self.tiley + 1
        if not ls.check_tile(x, y, TILE_LADDER):
            return
        self.mode = PLAYER_CLIMB
        tmp = self.partial_y + self.move_y
        if tmp & 1:
            self.move_y -= 1

    def hit_lift(self):
        if ls.lift_x is None:
            return

        if (ls.lift_x > self.x) or (ls.lift_x + 10 < self.x):
            return
        y1 = self.y - 0x11
        y2 = self.y - 0x13 + self.move_y
        tmp = ls.lift_y[0]
        if (tmp > y1) or (tmp < y2):
            tmp = ls.lift_y[1]
            if tmp != y1:
                if tmp >= y1:
                    return
                if tmp < y2:
                    return
            if ls.current_lift == 0:
                tmp += 1
        elif ls.current_lift != 0:
            tmp += 1
        tmp -= y1
        self.move_y = tmp + 1
        self.fall = 0
        self.mode = PLAYER_LIFT

    def jump(self):
        self.move_x = self.slide
        tmp2 = self.move_y
        tmp = self.fall >> 2
        if tmp >= 6:
            tmp = 6
        self.move_y = 2 - tmp
        self.fall += 1
        if self.y == 0xdc:
            self.move_y = -1
            self.fall = 0x0c
        else:
            self.grab_ladder(tmp2)
            if self.mode == PLAYER_CLIMB:
                return

        tmp = self.move_y + self.partial_y
        if tmp == 0:
            x = self.tilex
            y = self.tiley - 1
            if ls.check_tile(x, y, TILE_WALL):
                self.mode = PLAYER_WALK
        elif tmp > 0:
            if tmp == 8:
                x = self.tilex
                y = self.tiley
                if ls.check_tile(x, y, TILE_WALL):
                    self.mode = PLAYER_WALK
        else:
            x = self.tilex
            y = self.tiley - 1
            if ls.check_tile(x, y, TILE_WALL):
                self.mode = PLAYER_WALK
                self.move_y = -self.partial_y

        self.hit_lift()
        if self.mode == PLAYER_LIFT:
            return

        if self.blocked():
            self.move_x = -self.move_x
            self.slide = self.move_x

    def start_jump(self):
        self.button_ack |= 0x10
        self.fall = 0
        self.mode = PLAYER_JUMP
        tmp = self.move_x
        self.slide = tmp
        if tmp != 0:
            self.face = tmp
        self.jump()

    def move(self):
        self.move_x = 0
        self.move_y = 0
        if g.buttons & BUTTON_RIGHT:
            self.move_x += 1
        if g.buttons & BUTTON_LEFT:
            self.move_x -= 1
        if g.buttons & BUTTON_DOWN:
            self.move_y -= 1
        if g.buttons & BUTTON_UP:
            self.move_y += 1
        self.move_y <<= 1
        if self.mode == PLAYER_JUMP:
            self.jump()
        elif self.mode == PLAYER_FALL:
            self.fall += 1
            tmp = self.fall
            if tmp < 4:
                self.move_x = self.slide
                self.move_y = -1
            else:
                self.move_x = 0
                tmp = self.fall >> 2
                if tmp > 3:
                    tmp = 3
                self.move_y = -(tmp + 1)
            tmp = self.move_y + self.partial_y
            if tmp == 0:
                x = self.tilex
                y = self.tiley - 1
                if ls.check_tile(x, y, TILE_WALL):
                    self.mode = PLAYER_WALK
            elif tmp < 0:
                x = self.tilex
                y = self.tiley - 1
                if ls.check_tile(x, y, TILE_WALL):
                    self.mode = PLAYER_WALK
                    self.move_y = -self.partial_y
        elif self.mode == PLAYER_CLIMB:
            if (g.buttons & BUTTON_JUMP) != 0:
                self.start_jump()
            else:
                if (self.move_x != 0) and (self.partial_y == 0):
                    x = self.tilex
                    y = self.tiley - 1
                    if ls.check_tile(x, y, TILE_WALL):
                        self.move_y = 0
                        self.mode = PLAYER_WALK
                if self.mode != PLAYER_WALK:
                    self.move_x = 0
                    if (self.move_y != 0) and (self.partial_y == 0):
                        if self.move_y >= 0:
                            x = self.tilex
                            y = self.tiley + 2
                            if not ls.check_tile(x, y, TILE_LADDER):
                                self.move_y = 0
                        else:
                            x = self.tilex
                            y = self.tiley - 1
                            if not ls.check_tile(x, y, TILE_LADDER):
                                self.move_y = 0
                self.face = 0
        elif self.mode == PLAYER_LIFT:
            if (g.buttons & BUTTON_JUMP) != 0:
                self.start_jump()
            else:
                if (ls.lift_x > self.x) or (ls.lift_x + 9 < self.x):
                    self.fall = 0
                    self.slide = 0
                    self.mode = PLAYER_FALL
                self.move_y = 1
                if self.move_x != 0:
                    self.face = self.move_x
                if self.blocked():
                    self.move_x = 0
                if self.y >= 0xdc:
                    ls.is_dead += 1
        elif self.mode == PLAYER_WALK:
            if g.buttons & BUTTON_JUMP:
                self.start_jump()
            else:
                if self.move_y != 0:
                    if self.partial_x == 3:
                        x = self.tilex
                        if self.move_y >= 0:
                            y = self.tiley + 2
                        else:
                            y = self.tiley - 1
                        if ls.check_tile(x, y, TILE_LADDER):
                            self.move_x = 0
                            self.mode = PLAYER_CLIMB
                if self.mode == PLAYER_WALK:
                    self.move_y = 0
                    tmp = self.partial_x + self.move_x
                    x = self.tilex
                    if tmp < 0:
                        x -= 1
                    elif tmp >= 8:
                        x += 1
                    y = self.tiley - 1
                    if not ls.check_tile(x, y, TILE_WALL):
                        # Walk off edge
                        n = (self.move_x + self.partial_x) & 7
                        if n < 4:
                            x = 1
                            y = 1
                        else:
                            y = 0
                            x = -1
                        self.slide = x
                        self.fall = y
                        self.mode = PLAYER_FALL
                    if self.blocked():
                        self.move_x = 0
                    if self.move_x:
                        self.face = self.move_x
        else:
            raise Exception("Bad player mode")
        self.animate()

    def make_sound(self):
        if (self.move_x == 0) and (self.move_y == 0):
            return
        if (ls.duck_timer & 1) != 0:
            return
        if self.mode == PLAYER_WALK:
            tmp = 64
        elif self.mode == PLAYER_CLIMB:
            tmp = 96
        elif self.mode == PLAYER_JUMP:
            if self.fall >= 0x0b:
                tmp = 0xbe - (self.fall * 2)
            else:
                tmp = 0x96 + (self.fall * 2)
        elif self.mode == PLAYER_FALL:
            tmp = 0x6e - (self.fall * 2)
        elif self.mode == PLAYER_LIFT:
            if self.move_x == 0:
                return
            tmp = 0x64
        beep(tmp)

    def maybe_extra_life(self):
        if not self.extra_life:
            return
        self.extra_life = False
        g.player_data.lives += 1


