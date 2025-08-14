import random

import Defines as D
from BoardState import BoardState
import visualization

def resourceProbability(board, intersection):
    rv = [0] * 5
    for hex in [board.board[h] for h in intersection.hexes]:
        if D.RESOURCE_PRODUCTION[hex.tile]:
            index = D.resourceIndex(D.RESOURCE_PRODUCTION[hex.tile])
            rv[index] = rv[index] + D.ODDS[hex.number]
    return rv

def score(board, intersection, verbose=False): 
    score = 0

    # Assumption: the extra advantages offset.  Roads opening up settlements, settlements/cities improving production, 
    #    knights moving the robber, monopoly stealing from opponents, hidden victory points.
    [brick, lumber, ore, grain, wool] = resourceProbability(board, intersection)
    if verbose:
        print("Resource Probabilities: ", brick, lumber, ore, grain, wool)

    # Development Card Potential = .63
    # 2 Road Building = 2 * 1/3  (2 Roads = 1/3 of a point)
    # 2 Monopoly = 2 * 1 (It's generally going to net you a victory point)
    # 2 Year of Plenty = 2 * 1 (Again, generally going to net you a victory point)
    # 7 Knights = 7 * 1/4 (Generally going to take 4 to win largest army?)
    # 5 Victory Cards = 5 * 1
    # Total = ((2/3) + 2 + 2 + 7/4 + 5) / 18) = .63
    score += .63 * (ore + wool + grain) / 3
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

players = ["Red", "Blue", "Yellow", "White"]
random.shuffle(players)
board = BoardState(players)

scores = []
for intersection in board.graph.sortedIntersections:
    scores.append((score(board, intersection), intersection.hexCoords[0]))

for (i, s) in sorted(scores):
    print ("Intersection: ", i, "Score: ", s, flush=True)

visualization.draw_board(board, 0.0)
