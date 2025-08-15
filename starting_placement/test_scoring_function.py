import random

import Defines as D
from BoardState import BoardState
import visualization
import coordinate_chart

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
    # 7 Knights = 7 * 2/4 (Generally going to take 4 to win largest army?)
    # 5 Victory Cards = 5 * 1
    # Total = ((2/3) + 2 + 2 + 7/4 + 5) / 18) = 1.26
    dcp_score = 0
    for resource in [ore, wool, grain]:
        if resource == 0.0:
            dcp_score -= 1
    if dcp_score == 0:
        dcp_score = 1 + (ore + wool + grain) * 10
    score += 1.26 * dcp_score / 3
    if verbose:
        print("Score from DCP: ",  1.26 * dcp_score / 3)

    # Settlement Potential = 1
    settlement_score = 0
    for resource in [brick, lumber, wool, grain]:
        if resource == 0.0:
            settlement_score -= 1
    if settlement_score == 0:
        settlement_score = 1 + (brick + lumber + wool + grain) * 10
    score += 1 * settlement_score / 4
    if verbose:
        print("Score from Settlement Potential: ", 1 *  settlement_score / 4)

    # City Potential = 1
    city_score = 0
    for resource in [ore, ore, grain, grain, grain]:
        if resource == 0.0:
            city_score -= 1
    if city_score == 0:
        city_score = 1 + (ore + ore + grain + grain + grain) * 10
    score += 1 * city_score / 5
    if verbose:
        print("Score from City Potential: ", 1 *  city_score / 5)

    # Road Potential = 2/6 (Roughly 6 roads to win longest road?)
    road_score = 0
    for resource in [brick, lumber]:
        if resource == 0.0:
            road_score -= 1
    if road_score == 0:
        road_score = 1 + (brick + lumber) * 10
    score += (2/6) * road_score / 2
    if verbose:
        print("Score from Road Potential: ", (2/6) * brick * lumber)
    
    return [dcp_score, settlement_score, city_score, road_score]

players = ["Red", "Blue", "Yellow", "Green"]
random.shuffle(players)
board = BoardState(players)

chart_data = []
group_sizes = []
for intersection in board.graph.sortedIntersections:
    group_sizes.append(len(intersection.hexes))
    rp = resourceProbability(board, intersection)
    s = score(board, intersection)
    for h in intersection.hexes:
        hex = board.board[h]
        p = rp[D.resourceIndex(D.RESOURCE_PRODUCTION[hex.tile])] if D.RESOURCE_PRODUCTION[hex.tile] else 0
        chart_data.append([intersection.hexCoords[0], hex.tile, hex.number, f"{p:.4f}"] + [f"{x:.4f}" for x in s])

coordinate_chart.create_grid_chart(len(group_sizes), group_sizes, chart_data)