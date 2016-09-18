from .common import *

digit = [
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x90,0x90,0x90,0x90,0x60])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x20,0x60,0x20,0x20,0x20,0x20,0x70])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x10,0x20,0x40,0x80,0xf0])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x10,0x20,0x10,0x90,0x60])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x80,0x80,0xa0,0xa0,0xf0,0x20,0x20])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0xf0,0x80,0xe0,0x10,0x10,0x90,0x60])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x80,0xe0,0x90,0x90,0x60])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0xf0,0x10,0x10,0x20,0x20,0x40,0x40])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x90,0x60,0x90,0x90,0x60])
    ),
    Sprite(
	0x08, 0x07, BLACK,
	bytes([0x60,0x90,0x90,0x70,0x10,0x90,0x60])
    )
]

score = Sprite(
    0x18, 0x09, PURPLE,
    bytes([0xff,0xff,0xf8,0x88,0x89,0x88,0xbb,0xaa,0xb8,0xbb,0xaa,0xb8,0x8b,0xa9,0x98,0xeb,0xaa,0xb8,0xeb,0xaa,0xb8,0x88,0x8a,0x88,0xff,0xff,0xf8])
)
blank = Sprite(
    0x20, 0x09, PURPLE,
    bytes([0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe,0xff,0xff,0xff,0xfe])
)
player = Sprite(
    0x20, 0x09, PURPLE,
    bytes([0xff,0xff,0xff,0xff,0x9b,0xda,0x89,0xff,0xab,0xaa,0xba,0xff,0xab,0xaa,0xba,0xff,0x9b,0x8d,0x99,0xff,0xbb,0xad,0xba,0xff,0xbb,0xad,0xba,0xff,0xb8,0xad,0x8a,0xff,0xff,0xff,0xff,0xff])
)
level = Sprite(
    0x28, 0x09, PURPLE,
    bytes([0xff,0xff,0xff,0xff,0xfc,0xb8,0xa8,0xbf,0xff,0xfc,0xbb,0xab,0xbf,0xff,0xfc,0xbb,0xab,0xbf,0xff,0xfc,0xb9,0xa9,0xbf,0xff,0xfc,0xbb,0xab,0xbf,0xff,0xfc,0xbb,0xdb,0xbf,0xff,0xfc,0x88,0xd8,0x8f,0xff,0xfc,0xff,0xff,0xff,0xff,0xfc])
)
bonus = Sprite(
    0x30, 0x09, PURPLE,
    bytes([0xff,0xff,0xff,0xff,0xff,0xf0,0x98,0xb5,0x47,0xff,0xff,0xf0,0xaa,0x95,0x5f,0xff,0xff,0xf0,0xaa,0x95,0x5f,0xff,0xff,0xf0,0x9a,0xa5,0x47,0xff,0xff,0xf0,0xaa,0xa5,0x77,0xff,0xff,0xf0,0xaa,0xb5,0x77,0xff,0xff,0xf0,0x98,0xb4,0x47,0xff,0xff,0xf0,0xff,0xff,0xff,0xff,0xff,0xf0])
)
time = Sprite(
    0x28, 0x09, PURPLE,
    bytes([0xff,0xff,0xff,0xff,0xc0,0x8a,0x48,0xff,0xff,0xc0,0xda,0x4b,0xff,0xff,0xc0,0xda,0xab,0xff,0xff,0xc0,0xda,0xa9,0xff,0xff,0xc0,0xda,0xab,0xff,0xff,0xc0,0xda,0xeb,0xff,0xff,0xc0,0xda,0xe8,0xff,0xff,0xc0,0xff,0xff,0xff,0xff,0xc0])
)
hat = Sprite(
    0x08, 0x03, YELLOW,
    bytes([0x40,0xe0,0x00])
)