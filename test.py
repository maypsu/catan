import random
import time

from BoardState import BoardState
import Defines as D
import IntersectionGraph as IG
import starting_placement.dumbUtils as dumbUtils
import starting_placement.ModelBot as ModelBot
import visualization

def playGame(bots):
    start_time = time.time()

    players = ["Red", "Blue", "Yellow", "White"]
    random.shuffle(players)
    board = BoardState(players)

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

        resources = {}
        for hex in BoardState.graph.intersections[settlement].hexes:
            resource = board.board[hex].produces(board.board[hex].number)
        if resource: resources[resource] = resources.get(resource, 0) + 1

        board.players[player].addResources(resources)
        print ("Player %s starting with resources: %s" % (board.players[player].name, resources))

    for turn in range(0, 200):
        for pname in board.players:
            player = board.players[pname]
            print ("Turn %d Player %s" % (turn, player.name))
            if (player.developments):
                card = random.choice(player.developments)
                ds = 0
                for _ in range(0, 100):
                    ds += 1
                    if board.playDevelopment(player.name, card, dumbUtils.randomExtra(card, player.name, board)):
                        break

            # Produce
            # Pick a random spot for the robber to move
            robber = dumbUtils.randomRobber(pname, board)
            board.produce(pname, robber[0], robber[1])

            # Build
            if not dumbUtils.attemptBuild(player, board):
                # Trade
                choices = [x for x in D.RESOURCE_TYPES if player.canTrade(x)]
                if choices:
                    outgoing = random.choice(choices)
                    incoming = random.choice([x for x in D.RESOURCE_TYPES if x is not outgoing])
                    board.tradeMaritime(player.name, outgoing, incoming)

            print (board.strPlayers())
            if player.victory == 10:
                print ("VICTORY for %s" % player.name)
                print ("Elapsed Time:", str(time.time() - start_time))
                return player.name
        
    return "none"

bots = { "Red" : ModelBot.ModelBot("training_model_1.keras"), "Blue" : dumbUtils.DumbBot(), "Yellow" : dumbUtils.DumbBot(), "White" : dumbUtils.DumbBot() }

winners = {}
for _ in range(1000):
    winner = playGame(bots)
    winners[winner] = winners.get(winner, 0) + 1
print (winners)