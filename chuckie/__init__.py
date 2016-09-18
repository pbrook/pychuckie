#! /usr/bin/env python3

""" Chuckie Egg.
Based on the original by A & F Software
Written by Paul Brook
Released under the GNU GPL v3.
"""

import gc
from .constants import *
gc.collect()
from .playeractor import PlayerActor
gc.collect()
from .leveldata import leveldata
gc.collect()
from .levelstate import LevelState
gc.collect()
from . import g
import logging

log = logging.getLogger(__name__)

cheat = False

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
    global ls
    global cheat

    # New game
    g.player_data = PlayerData()
    while True:
        # New level
        ls = LevelState(g.player_data.level)
        g.ls = ls
        g.player = PlayerActor()

        while True:
            ui.poll()
            g.player.move()
            ui.sound()
            ls.move_lift()
            ls.move_ducks()
            g.player.maybe_extra_life()
            ls.collision_detect()
            ui.render()

            # if ((buttons & 0x80) != 0)
            #   goto new_game
            if ls.is_dead or (g.player.y < 0x11):
                log.info("Dead")
                # Died */
                # PlayTune(0x2fa6)
                g.player_data.lives -= 1
                break

            if (ls.eggs_left == 0) or cheat:
                log.info("Level Complete")
                # Level complete
                g.player_data.add_score(g.player_data.bonus)
                # Advance to next level
                cheat = False
                g.player_data.level += 1
                g.player_data.reset()
                break
