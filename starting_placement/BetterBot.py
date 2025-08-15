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

    def pickRoad(self, pname, board, first=None):
        # 
        existing_roads = [k for k, v in board.roads.items() if v == pname]
        if first: existing_roads.append(first)

        known_intersections = []
        for r in existing_roads:
            for i in sorted(r.adjacent):
                if (i not in board.settlements or board.settlements[i] == pname) and (i not in board.cities or board.cities[i] == pname):
                    known_intersections.append(i)
        
        tip_roads = []
        for i in known_intersections:
            for (r, _) in sorted(i.adjacent):
                if r not in board.roads:
                    tip_roads.append((r, r, 0))

        tip_roads.sort()

        exhausted_roads = list(board.roads.keys())
        if first: exhausted_roads.append(first)

        scores = {}
        while tip_roads:
            (t, p, l) = tip_roads.pop(0)

            if t in exhausted_roads:
                continue

            score = 0
            # does it connect
            connect = True
            for i in sorted(t.adjacent):
                this_side = (i in board.settlements and board.settlements[i] == pname) or (i in board.cities and board.cities[i] == pname)
                for (r, _) in sorted(i.adjacent):
                    this_side = this_side or (r in board.roads and board.roads[r] == pname)
                
                connect = connect and this_side
            if connect:
                score += 1
            
            # does it connect to somewhere that could be fun?
            for i in sorted(t.adjacent):
                if i in known_intersections: continue  #we already know its fun
                if not i.blockedSettle(board.settlements | board.cities):  # we could build there
                    score += scoreIntersection(board, i)

            scores[p] = scores.get(p, 0) + (score / (l + 1))
            exhausted_roads.append(t)

            for i in sorted(t.adjacent):
                if i in known_intersections: continue
                if i in board.settlements or i in board.cities: continue
                for (r, _) in sorted(i.adjacent):
                    if r in exhausted_roads: continue
                    tip_roads.append((r, p, l + 1))

        tscores = [(v, k) for k, v in scores.items()]
        tscores.sort(key=lambda k: k[0], reverse=True)
        for (s, t) in tscores: print (s, t)

        if tscores: return tscores[0][1]
        else: return None
    
    def getUnblockedNeighbors(self, road, pname, board):
        unblockedNeighbors = []
        for intersection in road.adjacent:
            if intersection in board.settlements and board.settlements[intersection] != pname \
                or intersection in board.cities and board.cities[intersection] != pname:
                continue
            for (x, _) in intersection.adjacent:
                if not x.blockedRoad(board.roads):
                    unblockedNeighbors.append(x)
        return unblockedNeighbors

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

def resourceProbability(board, intersection):
    rv = [0] * 5
    for hex in [board.board[h] for h in intersection.hexes]:
        if D.RESOURCE_PRODUCTION[hex.tile]:
            index = D.resourceIndex(D.RESOURCE_PRODUCTION[hex.tile])
            rv[index] = rv[index] + D.ODDS[hex.number]
    return rv

def scoreIntersection(board, intersection, verbose=False): 
    score = 0

    if intersection.blockedSettle(board.settlements | board.cities):
        return 0

    # Assumption: the extra advantages offset.  Roads opening up settlements, settlements/cities improving production, 
    #    knights moving the robber, monopoly stealing from opponents, hidden victory points.
    [brick, lumber, ore, grain, wool] = resourceProbability(board, intersection)
    if verbose:
        print("Resource Probabilities: ", brick, lumber, ore, grain, wool)

    # Development Card Potential = .63
    # 2 Road Building = 2 * 1/3  (2 Roads = 1/3 of a point)
    # 2 Monopoly = 2 * 1 (It's generally going to net you a victory point)
    # 2 Year of Plenty = 2 * 1 (Again, generally going to net you a victory point)
    # 7 Knights = 7 * 2/4 (Generally going to take 4 to win largest army?)
    # 5 Victory Cards = 5 * 1
    # Total = ((2/3) + 2 + 2 + 7/4 + 5) / 18) = 1.26
    score += 1.26 * (ore + wool + grain) / 3
    if verbose:
        print("Score from DCP: ", .63 * (ore + wool + grain) / 3)

    # Settlement Potential = 1
    score += 1 * (brick + lumber + wool + grain) / 4
    if verbose:
        print("Score from Settlement Potential: ", 1 * (brick + lumber + wool + grain) / 4)

    # City Potential = 1
    score += 1 * (2 * ore + 3 * grain) / 5
    if verbose:
        print("Score from City Potential: ", 1 * (2 * ore + 3 * grain) / 5)

    # Road Potential = 1/6 (Roughly 6 roads to win longest road?)
    score += (1/6) * (brick + lumber) / 2
    if verbose:
        print("Score from Road Potential: ", (1/6) * (brick + lumber) / 2)
    
    return score

    

