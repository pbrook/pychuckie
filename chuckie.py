#! /usr/bin/env python3

""" Chuckie Egg.
Based on the original by A & F Software
Written by Paul Brook
Released under the GNU GPL v3.
"""

import levels
import logging

log = logging.getLogger(__name__)

cheat = False


TILE_WALL = 1
TILE_LADDER = 2
TILE_EGG = 4
TILE_GRAIN = 8

DIR_L = 1
DIR_R = 2
DIR_UP = 4
DIR_DOWN = 8
DIR_HORIZ = 3
DIR_VERT = 0xc

PLAYER_WALK = 0
PLAYER_CLIMB = 1
PLAYER_JUMP = 2
PLAYER_FALL = 3
PLAYER_LIFT = 4

DUCK_BORED = 0
DUCK_STEP = 1
DUCK_EAT1 = 2
DUCK_EAT2 = 3
DUCK_EAT3 = 4
DUCK_EAT4 = 5

buttons = 0
BUTTON_LEFT = 1
BUTTON_RIGHT = 2
BUTTON_UP = 4
BUTTON_DOWN = 8
BUTTON_JUMP = 0x10

"""
/*        N    T  PI1  PI2  PI3  PN1  PN2  PN3   AA   AD   AS   AR  ALA  ALD */
/* E1: 0x01 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x7e 0xce 0x00 0x00 0x64 0x00
 * E2: 0x02 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x7e 0xfe 0x00 0xfb 0x7e 0x64
 * E3: 0x03 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x32 0x00 0x00 0xe7 0x64 0x00
 */
static void beep(int tmp) /* 0x0c98 */
{
  /* channel = 13 (Flush), note = 1, pitch = tmp, duration = 0x0001 */
  sound_start(tmp, 1)
}

static void squidge(int tmp) /* 0x0ca8 */
{
  /* 0001 0003 0000 0004 */
  sound_start(tmp, 0)
}
"""


def squidge(n):
    pass


class BigDuck():
    def __init__(self, active):
        self.x = 4
        self.y = 0xcc
        self.dx = 0
        self.dy = 0
        self.frame = 0
        self.dir = 0
        self.active = active

    def move(self):
        self.frame = 1 - self.frame
        if not self.active:
            return

        tmp = self.x + 4
        if tmp < player.x:
            if self.dx < 5:
                self.dx += 1
            self.dir = 0
        else:
            if self.dx > -5:
                self.dx -= 1
            self.dir = 1
        tmp = player.y + 4
        if tmp >= self.y:
            if self.dy < 5:
                self.dy += 1
        elif self.dy > -5:
            self.dy -= 1
        tmp = self.y + self.dy
        if tmp < 0x28:
            self.dy = -self.dy
        tmp = self.x + self.dx
        if (tmp < 0) or (tmp >= 0x90):
            self.dx = -self.dx
        self.x += self.dx
        self.y += self.dy

    def collision(self):
        if not self.active:
            return False

        if abs(self.x + 4 - player.x) > 5:
            return False
        if abs(self.y - 5 - player.y) > 14:
            return False
        return True


class LevelState():
    def __init__(self, current_level):
        log.info("Starting Level %d", current_level)
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

        level = levels.leveldata[current_level % 8]
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
            if not player_data.egg[i]:
                self.set_tile(x, y, (i << 4) | TILE_EGG)
                self.eggs_left += 1

        for i, (x, y) in enumerate(level['grain']):
            if not player_data.grain[i]:
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
            if player_data.bonus > 0:
                player_data.bonus -= 10
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
            if (abs(duck.x - player.x) <= 5) and \
                    (abs(duck.y - 1 - player.y) <= 14):
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
        self.levelmap[x + y * 20] |= val

    def clear_tile(self, x, y):
        self.levelmap[x + y * 20] = 0


class PlayerActor():
    def __init__(self):
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
            player_data.egg[n] = True
            ls.clear_tile(x, y)
            tmp = min((player_data.level >> 2) + 1, 10)
            player_data.add_score(tmp * 100)
        elif ls.check_tile(x, y, TILE_GRAIN):
            # Got grain
            squidge(5)
            n = ls.read_tile(x, y) >> 4
            player_data.grain[n] = True
            ls.clear_tile(x, y)
            player_data.add_score(50)
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
        if buttons & BUTTON_RIGHT:
            self.move_x += 1
        if buttons & BUTTON_LEFT:
            self.move_x -= 1
        if buttons & BUTTON_DOWN:
            self.move_y -= 1
        if buttons & BUTTON_UP:
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
            if (buttons & BUTTON_JUMP) != 0:
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
            if (buttons & BUTTON_JUMP) != 0:
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
            if buttons & BUTTON_JUMP:
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
        player_data.lives += 1


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
        if self.mode == DUCK_BORED:
            # Figure out which way to go next
            x = self.tilex
            y = self.tiley
            newdir = 0
            if ls.check_tile(x - 1, y - 1, TILE_WALL):
                newdir |= DIR_L
            if ls.check_tile(x + 1, y - 1, TILE_WALL):
                newdir |= DIR_R
            if ls.check_tile(x, y - 1, TILE_LADDER):
                newdir |= DIR_DOWN
            if ls.check_tile(x, y + 2, TILE_LADDER):
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
                newdir = tmp & ls.duck_random()
            self.dir = newdir

            # Check for grain to eat.
            tmp = self.dir
            if (tmp & DIR_HORIZ) != 0:
                if tmp == DIR_L:
                    x -= 1
                else:
                    x += 1
                if ls.check_tile(x, y, TILE_GRAIN):
                    self.mode = DUCK_EAT1
        if self.mode == DUCK_EAT2:
            # Eat grain
            x = self.tilex - 1
            y = self.tiley
            if self.dir == DIR_R:
                x += 2
            if ls.check_tile(x, y, TILE_GRAIN):
                n = ls.read_tile(x, y) >> 4
                player_data.grain[n] = True
                ls.clear_tile(x, y)
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


class PlayerData():
    def __init__(self):
        self.lives = 5
        self.level = 0
        self.score = 0
        self.reset()

    def add_score(self, amount):
        self.lives += ((self.score % 10000) + amount) // 10000
        self.score += amount

    def reset(self):
        self.bonus = 1000 * min(self.level + 1, 9)
        self.egg = [False] * 16
        self.grain = [False] * 16


def run_game(ui):
    global player_data
    global ls
    global player
    global cheat

    # New game
    player_data = PlayerData()
    while True:
        # New level
        ls = LevelState(player_data.level)
        player = PlayerActor()

        while True:
            ui.poll()
            player.move()
            ui.sound()
            ls.move_lift()
            ls.move_ducks()
            player.maybe_extra_life()
            ls.collision_detect()
            ui.render()

            # if ((buttons & 0x80) != 0)
            #   goto new_game
            if ls.is_dead or (player.y < 0x11):
                log.info("Dead")
                # Died */
                # PlayTune(0x2fa6)
                player_data.lives -= 1
                break

            if (ls.eggs_left == 0) or cheat:
                log.info("Level Complete")
                # Level complete
                player_data.add_score(player_data.bonus)
                # Advance to next level
                cheat = False
                player_data.level += 1
                player_data.reset()
                break
