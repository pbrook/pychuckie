from . import g

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
        if tmp < g.player.x:
            if self.dx < 5:
                self.dx += 1
            self.dir = 0
        else:
            if self.dx > -5:
                self.dx -= 1
            self.dir = 1
        tmp = g.player.y + 4
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

        if abs(self.x + 4 - g.player.x) > 5:
            return False
        if abs(self.y - 5 - g.player.y) > 14:
            return False
        return True


