import Defines as D
class Hex:
    def __init__(self, q, r, tile, robber):
        self.q = q
        self.r = r
        self.coords = (q, r)

        self.tile = tile
        self.number = 0
        self.robber = robber

    def coord(self):
        return (self.q, self.r)

    def produces(self, roll):
        return None if self.robber or roll != self.number else D.RESOURCE_PRODUCTION[self.tile]

    def __str__(self):
        return "%s, %s, %d, %s" % ((self.q, self.r), self.tile, self.number, self.robber)