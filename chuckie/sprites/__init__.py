import gc
from .common import *
gc.collect()
from .background import *
gc.collect()
from .player import *
gc.collect()
from .bigduck import *
gc.collect()
from .duck import *
gc.collect()
from .hud import *
gc.collect()

def init(load):
    for s in all_sprites:
        s.render = load(s)

duck = [
    duck_r,
    duck_r2,
    duck_l,
    duck_l2,
    duck_up,
    duck_up2,
    duck_eat_r,
    duck_eat_r2,
    duck_eat_l,
    duck_eat_l2,
]

bigduck_l = [
    bigduck_l1,
    bigduck_l2
]

bigduck_r = [
    bigduck_r1,
    bigduck_r2
]

player_r = [
    player_r1,
    player_r2,
    player_r1,
    player_r3
]

player_l = [
    player_l1,
    player_l2,
    player_l1,
    player_l3
]

player_up = [
    player_up1,
    player_up2,
    player_up1,
    player_up3
]
