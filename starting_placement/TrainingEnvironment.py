import numpy as np

import Defines as D
from .dumbUtils import initialPlace

class TrainingEnvironment:
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.turns = players + list(reversed(players))
        self._simulatePlayers()

    def _simulatePlayers(self):
        while len(self.turns) > 0:
            next = self.turns.pop(0)
            if (next == "Red"):
                return False

            initialPlace(self.board.players[next], self.board)
        return True

    def state(self):
        board = self.board
        state = []
        players = [0] * len(self.players)
        players[self.players.index("Red")] = 1

        sortedHexes = sorted(board.board)
        for hex in sortedHexes:
            # tile type
            tile = [0] * 6
            tile[D.tileIndex(board.board[hex].tile)] = 1
            # tile number
            number = board.board[hex].number / 12
            state.extend(tile + [number])

        for intersection in board.graph.sortedIntersections:
            settled = [0] * len(self.players)
            if intersection in board.settlements:
                pname = board.settlements[intersection]
                settled[self.players.index(pname)] = 1
            elif intersection in board.cities:
                pname = board.cities[intersection]
                settled[self.players.index(pname)] = 1
            state.extend(settled)

        for path in board.graph.sortedPaths:
            settled = [0] * len(self.players)
            if path in board.roads:
                pname = board.roads[path]
                settled[self.players.index(pname)] = 1
            state.extend(settled)

        return np.array(state, dtype=np.float32)

    def step(self, action):
        intersection, path = action
        coordinate = self.board.graph.sortedIntersections[intersection].hexCoords[0]
        self.board.buildSettle("Red", coordinate, start=True, verbose=False)
        road = self.board.graph.sortedPaths[path].hexCoords[0]
        self.board.buildRoad("Red", road, start=True, verbose=False)
        
        done = self._simulatePlayers()
        reward = 0 if not done else self.reward("Red")

        return self.state(), reward, done

    def reward(self, pname):
        score = 0

        # Assumption: the extra advantages offset.  Roads opening up settlements, settlements/cities improving production, 
        #    knights moving the robber, monopoly stealing from opponents, hidden victory points.
        [brick, lumber, ore, grain, wool] = self.board.playerResourceProbability(pname)

        # Development Card Potential = .63
        # 2 Road Building = 2 * 1/3  (2 Roads = 1/3 of a point)
        # 2 Monopoly = 2 * 1 (It's generally going to net you a victory point)
        # 2 Year of Plenty = 2 * 1 (Again, generally going to net you a victory point)
        # 7 Knights = 7 * 1/4 (Generally going to take 4 to win largest army?)
        # 5 Victory Cards = 5 * 1
        # Total = ((2/3) + 2 + 2 + 7/4 + 5) / 18) = .63
        score += .63 * (ore + wool + grain) / 3

        # Settlement Potential = 1
        score += 1 * (brick + lumber + wool + grain) / 4

        # City Potential = 1
        score += 1 * (2 * ore + 3 * grain) / 5

        # Road Potential = 1/6 (Roughly 6 roads to win longest road?)
        score += (1/6) * (brick + lumber) / 2

        # Road Connection Distance - is this too much of a bonus?
        score += .1 * (1 - (self.board.roadConnectionDistance(pname) / 4))

        return score