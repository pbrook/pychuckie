import pygame

def init():
    global surf
    surf = pygame.display.get_surface()

rpal = {}
palette = []
stream_x = 0
stream_y = 0

def html_color(val):
    if val in rpal:
        return rpal[val]
    i = len(palette)
    palette.append(pygame.Color((val << 8) | 0xff))
    rpal[val] = i
    return i

def line(x1, y1, x2, y2, color):
    surf.set_at((x1, y1), palette[color])


def stream_start(x, y, w, h):
    global stream_x
    global stream_y
    stream_x = x
    stream_y = y

def stream_stop():
    pass

def stream_color(color):
    global stream_x
    surf.set_at((stream_x, stream_y), palette[color])
    stream_x += 1
