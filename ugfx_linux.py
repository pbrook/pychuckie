import pygame

def init():
    global surf
    surf = pygame.display.get_surface()

rpal = {}
palette = []

def html_color(val):
    if val in rpal:
        return rpal[val]
    i = len(palette)
    palette.append(pygame.Color((val << 8) | 0xff))
    rpal[val] = i
    return i

def line(x1, y1, x2, y2, color):
    surf.set_at((x1, y1), palette[color])

