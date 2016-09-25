#SpriteColor = collections.namedtuple("SpriteColor", "r g b")

from .. import sprite_base

class SpriteColor():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

GREEN = SpriteColor(0, 255, 0)
PURPLE = SpriteColor(255, 0, 255)
YELLOW = SpriteColor(255, 255, 0)
BLUE = SpriteColor(0, 0, 255)
BLACK = SpriteColor(0, 0, 0)

all_sprites = []

Sprite = sprite_base.Sprite
