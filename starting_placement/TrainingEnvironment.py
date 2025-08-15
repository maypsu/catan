import numpy as np

import Defines as D

class TrainingEnvironment:
    def __init__(self, board, players, bot):
        self.board = board
        self.players = players
        self.bot = bot

        self.turns = players + list(reversed(players))
        self._simulatePlayers(verbose=False)

    def _simulatePlayers(self, verbose=False):
        while len(self.turns) > 0:
            next = self.turns.pop(0)
            if (next == "Red"):
                return False

            settlement, road = self.bot.initialPlace(self.board.players[next], self.board)
            if not self.board.buildSettle(next, settlement, True, verbose=verbose): 
                raise Exception(f"Could not place SETTLEMENT at determined coordinates {settlement}")
    
            if not self.board.buildRoad(next, road, True, verbose=verbose): 
                raise Exception(f"Could not place ROAD at determined coordinates {road}")
            
        return True

    def state(self):
        return self.board.state()

    def step(self, action, verbose=False):
        intersection, path = action
        coordinate = self.board.graph.sortedIntersections[intersection].hexCoords[0]
        if not self.board.buildSettle("Red", coordinate, start=True, verbose=verbose):
            raise Exception(f"RED tried to settle at {coordinate} but was blocked")
        road = self.board.graph.sortedPaths[path].hexCoords[0]
        if not self.board.buildRoad("Red", road, start=True, verbose=verbose):
            raise Exception(f"RED tried to pave at {road} but was blocked")
        
        done = self._simulatePlayers(verbose=verbose)
        reward = 0 if not done else self.reward("Red")

        return self.state(), reward, done

    def reward(self, pname, verbose=False):
        # Assumption: the extra advantages offset.  Roads opening up settlements, settlements/cities improving production, 
        #    knights moving the robber, monopoly stealing from opponents, hidden victory points.
        [brick, lumber, ore, grain, wool] = self.board.playerResourceProbability(pname)
        if verbose:
            print("Resource Probabilities: ", brick, lumber, ore, grain, wool)

        
        potential_score = 0
        # Development Card Potential = .63
        # 2 Road Building = 2 * 1/3  (2 Roads = 1/3 of a point)
        # 2 Monopoly = 2 * 1 (It's generally going to net you a victory point)
        # 2 Year of Plenty = 2 * 1 (Again, generally going to net you a victory point)
        # 7 Knights = 7 * 2/4 (Generally going to take 4 to win largest army?)
        # 5 Victory Cards = 5 * 1
        # Total = ((2/3) + 2 + 2 + 7/4 + 5) / 18) = 1.26
        potential_score += 1.26 * (ore + wool + grain) / 3
        if verbose:
            print("Score from DCP: ", .63 * (ore + wool + grain) / 3)

        # Settlement Potential = 1
        potential_score += 1 * (brick + lumber + wool + grain) / 4
        if verbose:
            print("Score from Settlement Potential: ", 1 * (brick + lumber + wool + grain) / 4)

        # City Potential = 1
        potential_score += 1 * (2 * ore + 3 * grain) / 5
        if verbose:
            print("Score from City Potential: ", 1 * (2 * ore + 3 * grain) / 5)

        # Road Potential = 1/6 (Roughly 6 roads to win longest road?)
        potential_score += (1/6) * (brick + lumber) / 2
        if verbose:
            print("Score from Road Potential: ", (1/6) * (brick + lumber) / 2)

        # Road Connection Distance - is this too much of a bonus?
        #score += .1 * (1 - (self.board.roadConnectionDistance(pname) / 4))
        #if verbose:
        #    print("Score from RCD: ", .1 * (1 - (self.board.roadConnectionDistance(pname) / 4)))

        #  Edge Guard
        for settlement in [k for k, v in self.board.settlements.items() if v == pname]:
            if len(settlement.adjacent) < 3:
                potential_score -= .1

        return potential_score