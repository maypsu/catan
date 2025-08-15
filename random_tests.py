import argparse
import numpy as np
import random

import BoardState
import starting_placement.TrainingEnvironment as TE
import starting_placement.ModelBot as ModelBot
import starting_placement.RandoBot as RandoBot
import visualization

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="fooling.keras", type=str)
    return parser.parse_args()

args = parseArguments()
bots = { "Red" : ModelBot.ModelBot(args.input), "Blue" : RandoBot.RandoBot(), "Yellow" : RandoBot.RandoBot(), "Green" : RandoBot.RandoBot() }

scores = {}
for i in range(10000):
    players = ["Red", "Blue", "Yellow", "Green"]
    random.shuffle(players)
    board = BoardState.BoardState(players)
    env = TE.TrainingEnvironment(board, players, bots["Red"])
    
    for player in board.players:
        settlement, road = bots[player].initialPlace(board.players[player], board)
        if not board.buildSettle(player, settlement, start=True, verbose=False): 
            raise Exception(f"Could not place SETTLEMENT at determined coordinates {settlement}")

        if not board.buildRoad(player, road, start=True, verbose=False): 
            raise Exception(f"Could not place ROAD at determined coordinates {road}")

    for player in reversed(board.players):
        settlement, road = bots[player].initialPlace(board.players[player], board)
        if not board.buildSettle(player, settlement, start=True, verbose=False):
            raise Exception(f"Could not place SETTLEMENT at determined coordinates {settlement}")

        if not board.buildRoad(player, road, start=True, verbose=False): 
            raise Exception(f"Could not place ROAD at determined coordinates {road}")

    for player in players:
        score = env.reward(player)
        if player not in scores:
            scores[player] = []
        scores[player].append(score)

print ("Scores")
for player in players:
    print ("Player", player, "\tMin", f"{np.min(scores[player]):.4f}", "Max", f"{np.max(scores[player]):.4f}", "Ave", f"{np.mean(scores[player]):.4f}")

