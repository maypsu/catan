import Defines as D
class Player:
    def __init__(self, name):
        self.name = name

        # Initial resources
        self.resources = [0] * 5

        # Initial military
        self.military = 0

        # Initial development cards
        self.developments = []

        # Initial victory points
        self.victory = 0

        # Initial supply
        self.supply = [15, 5, 4]

        # Initial harbor access
        self.harbors = [False] * 6

    def addResources(self, resources):
        for type in resources:
            amount = resources[type]
            self.resources[D.resourceIndex(type)] += amount

    def removeResources(self, resources):
        for type in resources:
            amount = resources[type]
            self.resources[D.resourceIndex(type)] -= amount

    def canAffordResources(self, resources):
        for type in resources:
            amount = resources[type]
            if self.resources[D.resourceIndex(type)] < amount:
                return False
        return True
    
    def canTrade(self, resource):
        if self.harbors[D.harborIndex(resource)] and self.resources[D.resourceIndex(resource)] > 1:
            return True
        if self.harbors[D.harborIndex("Wild")] and self.resources[D.resourceIndex(resource)] > 2:
            return True
        if self.resources[D.resourceIndex(resource)] > 4:
            return True
        return False

    def __str__(self):
        return "%s\t(%d, %d): %s %s %s" % (self.name, self.victory, self.military,
                                        str(self.resources), str(self.developments), str(self.harbors))
    