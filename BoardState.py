from operator import truediv
import numpy as np
import random
from Hex import Hex
from Player import Player
import Defines as D
import IntersectionGraph as IG

# See https://www.redblobgames.com/grids/hexagons/implementation.html for explanation of hex grid

class BoardState:
    graph = IG.Graph()

    def __init__(self, pnames):
        self.play_order = pnames.copy()

        # Save off the players
        self.players = {}
        for pname in pnames:
            self.players[pname] = Player(pname)

        # initialize the board
        self.board = {}

        # Make copies so we can pop from the lists in the following loop
        tiles = D.TILES.copy()
        random.shuffle(tiles)

        # Build the hex grid for extent N = 2 giving each a random tile and number
        N = 2
        for q in range(-N, N + 1):
            for r in range(max(-N, -q - N), min(N, -q + N) + 1):
                tile = tiles.pop()
                self.board[(q, r)] = Hex(q, r, tile, tile == "Desert")

        # Place numbers in a spiral pattern
        placements = D.NUMBER_PLACEMENTS[random.randint(0, 5)]
        gridIndex, numberIndex = 0, 0
        while numberIndex < len(D.NUMBERS):
            coord = placements[gridIndex]
            if self.board[coord].tile == "Desert":
                gridIndex += 1
                coord = placements[gridIndex]
            self.board[coord].number = D.NUMBERS[numberIndex]
            gridIndex += 1
            numberIndex += 1

        # Set the development card deck
        self.developments = ["Road Building"] * 2 + ["Monopoly"] * 2 \
                            + ["Year of Plenty"] * 2 + ["Knight"] * 7 \
                            + [a for a in D.VICTORY_CARDS]
        random.shuffle(self.developments)

        self.roads = {}
        self.settlements = {}
        self.cities = {}

        self.largestArmy = None
        self.longestRoad = None

    def state(self):
        board = self

        board_state = []
        # Active Player is always us!
        players_state = [0] * len(self.play_order)
        players_state[self.play_order.index("Red")] = 1
        board_state.extend(players_state)

        # Add the hex information (6 tile types, 11 possible numbers)
        N = 2
        for q in range(-N, N + 1):
            for r in range(max(-N, -q - N), min(N, -q + N) + 1):
                hex = board.board[(q, r)]
                # tile type
                tile = [0] * 6
                tile[D.tileIndex(hex.tile)] = 1
                # tile number
                number = [0] * 11
                if hex.number == 0: # putting the 0 at 7 cause I'm lazy
                    number[5] = 1
                else:
                    number[hex.number - 2] = 1
                board_state.extend(tile + number)

        intersection_state = []
        for intersection in board.graph.sortedIntersections:
            settled = [0] * len(self.play_order)
            if intersection in board.settlements:
                pname = board.settlements[intersection]
                settled[self.play_order.index(pname)] = 1
            elif intersection in board.cities:
                pname = board.cities[intersection]
                settled[self.play_order.index(pname)] = 1
            intersection_state.extend(settled)

        path_state = []
        for path in board.graph.sortedPaths:
            settled = [0] * len(self.play_order)
            if path in board.roads:
                pname = board.roads[path]
                settled[self.play_order.index(pname)] = 1
            path_state.extend(settled)

        return board_state, intersection_state, path_state


    def buildSettle(self, pname, coordinate, start=False, verbose=True):
        player = self.players[pname]
        intersection = BoardState.graph.intersections[coordinate]

        # Has Settlements left
        if player.supply[D.supplyIndex("Settlement")] == 0: return False

        if (not start):
            # Can afford
            if not player.canAffordResources(D.supplyCost("Settlement")): return False

            # Can connect
            if not intersection.canConnect(pname, self.roads): return False

        # Something in the way
        if intersection.blockedSettle(self.settlements | self.cities): return False

        self.settlements[intersection] = pname
        if intersection.hexCoords[0] in D.HARBORS:
            player.harbors[D.harborIndex(D.HARBORS[intersection.hexCoords[0]])] = True

        player.supply[D.supplyIndex("Settlement")] -= 1
        player.victory += 1

        # Spend that money
        if not start :
            player.removeResources(D.supplyCost("Settlement"))

        if verbose:  
            print ("Player %s built settlement at %s" % (pname, intersection))

        return True
    
    
    def buildRoad(self, pname, coordinate, start=False, free=False, verbose=True):
        player = self.players[pname]
        path = BoardState.graph.paths[(coordinate)]
        # Has Roads left
        if player.supply[D.supplyIndex("Road")] == 0: return False

        if not start and not free:
            # Can afford
            if not player.canAffordResources(D.supplyCost("Road")): return False

        # Can connect
        if not free and not path.canConnect(pname, self.roads, self.settlements, start): return False

        # Something in the way
        if path.blockedRoad(self.roads): return False

        self.roads[path] = pname
        player.supply[D.supplyIndex("Road")] -= 1

        # Spend that money
        if not free and not start:
            player.removeResources(D.supplyCost("Road"))
        if verbose:
            print ("Player %s built road at %s" % (pname, path))

        self.computeLongestRoad(pname, verbose=verbose)

        return True

    def buildCity(self, pname, coordinate, verbose=True):
        player = self.players[pname]
        intersection = BoardState.graph.intersections[coordinate]

        #Can Afford
        if not player.canAffordResources(D.supplyCost("City")): return False

        # Has Cities left
        if player.supply[D.supplyIndex("City")] == 0: return False

        # Can connect
        if not intersection.canConnect(pname, self.roads): return False

        # Something in the way
        if intersection.blockedCity(pname, self.settlements): return False

        # Remove the Settlement
        del self.settlements[intersection]
        player.supply[D.supplyIndex("Settlement")] += 1

        # Place the City
        self.cities[intersection] = pname
        player.supply[D.supplyIndex("City")] -= 1

        # Spend that money
        player.removeResources(D.supplyCost("City"))
        player.victory += 1

        if verbose:
            print ("Player %s built city at %s" % (pname, intersection))

        return True

    def produce(self, pname, robber, verbose=True):
        roll = random.randint(1, 6) + random.randint(1, 6)
        if verbose:
            print ("Rolled", roll)

        if roll == 7:
            target, coords = robber.pickRobber(pname, self)
            self.robber(pname, target, coords, verbose=verbose)
            return

        playerProduction = {}
        for (intersection, pname) in self.settlements.items():
            for hex in intersection.hexes:
                resource = self.board[hex].produces(roll)
                if resource:
                    if not pname in playerProduction: playerProduction[pname] = {}
                    playerProduction[pname][resource] = playerProduction[pname].get(resource, 0) + 1

        for (intersection, pname) in self.cities.items():
            for hex in intersection.hexes:
                resource = self.board[hex].produces(roll)
                if resource:
                    if not pname in playerProduction: playerProduction[pname] = {}
                    playerProduction[pname][resource] = playerProduction[pname].get(resource, 0) + 1

        if verbose:
            print ("Produced:", playerProduction)
        for (pname, production) in playerProduction.items():
            self.players[pname].addResources(production)

    def robber(self, pname, target, hex, verbose=True):
        for h in self.board:
            self.board[h].robber = (h == hex)

        valid = False
        for intersection in BoardState.graph.sortedIntersections:
            if hex in intersection.hexes and (self.settlements.get(intersection) is target or self.cities.get(intersection) is target):
                valid = True

        if (valid):
            resources = []
            for i in range(0, len(D.RESOURCE_TYPES)):
                for _ in range(0, self.players[target].resources[i]):
                    resources.append(D.RESOURCE_TYPES[i])

            if len(resources) > 0:
                resource = random.choice(resources)
                self.players[target].resources[D.resourceIndex(resource)] -= 1
                self.players[pname].resources[D.resourceIndex(resource)] += 1
                if verbose:
                    print ("Robber stole %s from %s" % (resource, target))
        if verbose:
            print ("Robber is now blocking %s: %d - %s" % (hex, self.board[hex].number, self.board[hex].tile))

    def buyDevelopment(self, pname, verbose=True):
        player = self.players[pname]
        
        if not self.developments: return False
        if not player.canAffordResources(D.supplyCost("Development")): return False

        card = self.developments.pop()
        player.developments.append(card)

        player.removeResources(D.supplyCost("Development"))
        if verbose:
            print("Player %s drew a '%s'" % (pname, card))

    # Affect the board state by using the card
    def playDevelopment(self, pname, card, extras=[], verbose=True):
        player = self.players[pname]

        # Victory cards do nothing
        if card in D.VICTORY_CARDS:
            player.developments.remove(card)
            player.victory += 1
            if verbose:
                print("Player %s played victory card '%s'" % (pname, card))
            return True

        # Knights move the Robber
        # TODO - steal a resource
        if card == "Knight":
            player.developments.remove(card)
            player.military += 1
            self.robber(pname, extras[0], extras[1], verbose=verbose)
            if verbose:
                print("Player %s played a knight moving the robber to block %s at %s" % (pname, extras[0], extras[1]))
            if (self.largestArmy is None and player.military >= 3) \
                or (self.largestArmy is not None and player.military > self.players[self.largestArmy].military):
                if self.largestArmy: self.players[self.largestArmy].victory -= 2
                if verbose:
                    print ("Player %s now has the largest army with %d" % (pname, player.military))
                self.largestArmy = pname
                player.victory += 2
            return True

        # Road Building
        if card == "Road Building":
            roads = self.roads.copy()
            for coord in extras:
                path = BoardState.graph.paths[coord]

                # Can connect
                if not path.canConnect(pname, roads): return False

                # Something in the way
                if path.blockedRoad(roads): return False

                roads[path] = pname

            # If we made it this far without blocking, go ahead and set the board
            player.developments.remove(card)
            if verbose:
                print("Player %s played 'Road Building' for roads at %s and %s" % (pname, extras[0], extras[1]))

            self.roads.update(roads)

            return True

        if card == "Monopoly":
            type = extras[0]
            index = D.resourceIndex(type)

            player.developments.remove(card)
            count = 0
            stole = []
            for p in self.players:
                if p is not pname:
                    stole.append("%s %d" % (p, self.players[p].resources[index]))
                    count += self.players[p].resources[index]
                    self.players[p].resources[index] = 0

            player.resources[index] += count
            if verbose:
                print ("Player %s stole %d %s resources from: %s" % (pname, count, type, ", ".join(stole)))
            return True

        if card == "Year of Plenty":
            resources = {}
            for type in extras:
                resources[type] = resources.get(type, 0) + 1

            player.developments.remove(card)
            player.addResources(resources)
            if verbose:
                print ("Player %s played 'Year of Plenty' for %s" % (pname, extras))
            return True
        
        raise Exception("Attempted to play DevelopmentCard with unknown type: " + card)

    def executeTrade(self, player, opponent, give, take):
        player.addResourcesArray(take)
        opponent.addResourcesArray(give)

        player.removeResourcesArray(give)
        opponent.removeResourcesArray(take)

    def tradeMaritime(self, pname, outgoing, incoming, verbose=True):
        player = self.players[pname]
        count = 4
        if player.harbors[D.harborIndex(outgoing)] == True:
            count = 2
        elif player.harbors[D.harborIndex("Wild")] == True:
            count = 3

        if not player.canAffordResources({outgoing : count}):
            return False

        if verbose:
            print ("Player %s trading %d of %s for %s" % (pname, count, outgoing, incoming))
        player.removeResources({outgoing : count})
        player.addResources({incoming : 1})
        return True

    def computeLongestRoad(self, pname, verbose=True):
        playerRoads = {}
        for (path, owner) in self.roads.items():
            if owner not in playerRoads: playerRoads[owner] = []
            playerRoads[owner].append(path)
        
        maxLengths = {}
        for (owner, paths) in playerRoads.items():
            groups = []
            while len(paths) > 0:
                path = paths.pop()
                group = [path]
                intersections = list(path.adjacent)
                while len(intersections) > 0:
                    intersection = intersections.pop()
                    # Longest road is broken by opposing cities / settlements
                    if (intersection in self.settlements and self.settlements[intersection] is not pname) \
                        or (intersection in self.cities and self.cities[intersection] is not pname):
                        continue
                    for (p, _) in intersection.adjacent:
                        if p in paths:
                            paths.remove(p)
                            group.append(p)
                            intersections.extend(p.adjacent)
                groups.append(group)
            maxLengths[owner] = max([len(x) for x in groups])
        
        if self.longestRoad:
            if maxLengths[pname] > maxLengths[self.longestRoad]:
                if verbose:
                    print ("Player", pname, "has stolen the longest road from",  self.longestRoad, "with a length of", maxLengths[pname])
                self.players[pname].victory += 2
                self.players[self.longestRoad].victory -= 2
                self.longestRoad = pname
        else:
            if maxLengths[pname] >= 5:
                if verbose:
                    print ("Player", pname, "has the longest road with a length of", maxLengths[pname])
                self.players[pname].victory += 2
                self.longestRoad = pname

    def computeValidIntersectionPathPairs(self):
        pairs = []
        for i in range(len(self.graph.sortedIntersections)):
            intersection = self.graph.sortedIntersections[i]
            # If the intersection itself is occupied skip
            if intersection.blockedSettle(self.settlements | self.cities):
                continue

            for (path, _) in intersection.adjacent:
                # If the neighboring intersection is occupied skip
                if path.blockedRoad(self.roads):
                    continue

                pairs.append((i, self.graph.sortedPaths.index(path)))

        return pairs

    def playerResourceProbability(self, pname):
        rv = [0] * 5
        for intersection, p in self.settlements.items():
            if p == pname:
                for hex in [self.board[h] for h in intersection.hexes]:
                    if D.RESOURCE_PRODUCTION[hex.tile]:
                        index = D.resourceIndex(D.RESOURCE_PRODUCTION[hex.tile])
                        rv[index] = rv[index] + D.ODDS[hex.number]

        for intersection, p in self.cities.items():
            if p == pname:
                for hex in [self.board[h] for h in intersection.hexes]:
                    if D.RESOURCE_PRODUCTION[hex.tile]:
                        index = D.resourceIndex(D.RESOURCE_PRODUCTION[hex.tile])
                        rv[index] = rv[index] + (2 * D.ODDS[hex.number])

        # TODO: Harbors?
        return rv

    def roadConnectionDistance(self, pname):
        # TODO - handle more than two roads
        [start, finish] = [k for k, v in self.roads.items() if v == pname]
        neighbors = [(0, r) for r in start.adjacent] # Adjacent to paths are two intersections
        explored = set([start])
        distance = -1
        while neighbors:
            (cost, neighbor) = neighbors.pop(0)
            if finish in [r for (r, _) in neighbor.adjacent]: # Adjacent to intersections are 2-3 (path, intersection) pairs
                distance = cost
                break

            explored.update([neighbor])
            for (_, i) in neighbor.adjacent:
                if not i in explored:
                    neighbors.append((cost + 1, i))

        if distance == -1:
            raise Exception(f"Failed to find connection distance between {start} and {finish}")
        
        return distance


    def __str__(self):
        out = "\n".join([str(self.board[hex]) for hex in self.board]) + "\n"
        out += "\nRoads\n"
        players = {}
        for (x, y) in self.roads.items():
            if y not in players: players[y] = set()
            players[y].add(x)
        for (player, roads) in players.items():
            out += "%s (%d): %s\n" % (player, len(roads), ", ".join([str(x) for x in roads]))

        players.clear()
        out += "\nSettlements\n"
        for (x, y) in self.settlements.items():
            if y not in players: players[y] = set()
            players[y].add(x)
        for (player, settlements) in players.items():
            out += "%s (%d): %s\n" % (player, len(settlements), ", ".join([str(x) for x in settlements]))
    
        players.clear()
        out += "\nCities\n"
        for (x, y) in self.cities.items():
            if y not in players: players[y] = set()
            players[y].add(x)
        for (player, cities) in players.items():
            out += "%s (%d): %s\n" % (player, len(cities), ", ".join([str(x) for x in cities]))

        out += "\nDevelopment Cards: " + ", ".join([c for c in self.developments]) + "\n"
        out += "Longest Road: " + (self.longestRoad if self.longestRoad else "None") + "\n"
        out += "Largest Army: " + (self.largestArmy if self.largestArmy else "None") + "\n"
        out += "\nPlayers\n" + self.strPlayers()

        return out

    def strPlayers(self):
        out = "Name (Victory Points, Military Size): [Resources (Brick, Lumber, Ore, Grain, Wool)] [Development Cards] [Ports]\n"
        for pname in self.players:
            out += str(self.players[pname]) + "\n"

        return out
