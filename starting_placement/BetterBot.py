import random

import Defines as D

class BetterBot:
    def __init__(self):
        self.statistics = [0, 0, 0, 0]

    def initialPlace(self, player, board):
        while True:
            coordinate = pickRandom()
            intersection = board.graph.intersections[coordinate]
            if intersection.blockedSettle(board.settlements | board.cities):
                continue

            foundPath = None
            for (path, _) in intersection.adjacent:
                if not path.blockedRoad(board.roads):
                    foundPath = path
                    break
            
            if not foundPath:
                continue

            break
        return coordinate, foundPath.hexCoords[0]    

    def playCards(self, player, board, verbose=True):
        if (player.developments):
            card = random.choice(player.developments)
            ds = 0
            for _ in range(0, 100):
                ds += 1
                if board.playDevelopment(player.name, card, self.bot.randomExtra(card, player.name, board), verbose=verbose):
                    break


    def attemptBuild(self, player, board, verbose=True):
        pname = player.name
        if (player.canAffordResources(D.supplyCost("City")) and player.supply[2] > 0 and player.supply[1] < 5):
            for _ in range(0, 100):
                if board.buildCity(pname, pickRandom(), verbose=verbose):
                    self.statistics[2] += 1
                    return True

        if (player.canAffordResources(D.supplyCost("Settlement")) and player.supply[1] > 0):
            for _ in range(0, 100):
                if board.buildSettle(pname, pickRandom(), verbose=verbose):
                    self.statistics[1] += 1
                    return True

        if (player.canAffordResources(D.supplyCost("Road")) and player.supply[0] > 0):
            for _ in range(0, 100):
                if board.buildRoad(pname, pickRandom(), verbose=verbose):
                    self.statistics[0] += 1
                    return True

        if (player.canAffordResources(D.supplyCost("Development")) and board.developments):
            board.buyDevelopment(pname, verbose=verbose)
            self.statistics[3] += 1
            return True
        
        return False
    
    def pickRobber(self, pname, board):
        while True:
            (q, r, _) = pickRandom()
            robber = (q, r)

            producers = board.settlements | board.cities
            for x in range(0, 6):
                intersection = board.graph.intersections[(q, r, x)]
                if intersection in producers and producers[intersection] is not pname: 
                    return producers[intersection], robber

    def randomRoad(self, pname, start, board):
        while True:
            coordinate = pickRandom()
            path = board.graph.paths[coordinate]
            if path.canConnect(pname, board.roads, board.settlements, start):
                return coordinate

    def randomExtra(self, card, pname, board):
        if card in D.VICTORY_CARDS:
            return []
        if card == "Knight":
            return self.pickRobber(pname, board)
        if card == "Road Building":
            return [self.randomRoad(pname, False, board), self.randomRoad(pname, False, board)]
        if card == "Monopoly":
            return random.choices(D.RESOURCE_TYPES, k=1)
        if card == "Year of Plenty":
            return random.choices(D.RESOURCE_TYPES, k=2)

def pickRandom():
    while True:
        q = random.randint(-2, 2)
        r = random.randint(-2, 2)
        x = random.randint(0, 5)

        s = -q - r
        if s < -2 or s > 2:
            continue

        return (q, r, x)
    


    

