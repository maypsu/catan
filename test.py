import random
import time

from BoardState import BoardState
import Defines as D
import IntersectionGraph as IG
import starting_placement.RandoBot as RandoBot
import starting_placement.ModelBot as ModelBot
import visualization

def playGame(bots, verbose=True):

    players = ["Red", "Blue", "Yellow", "White"]
    random.shuffle(players)
    board = BoardState(players)

    for player in board.players:
        settlement, road = bots[player].initialPlace(board.players[player], board)
        if not board.buildSettle(player, settlement, start=True, verbose=verbose): 
            raise Exception(f"Could not place SETTLEMENT at determined coordinates {settlement}")

        if not board.buildRoad(player, road, start=True, verbose=verbose): 
            raise Exception(f"Could not place ROAD at determined coordinates {road}")

    for player in reversed(board.players):
        settlement, road = bots[player].initialPlace(board.players[player], board)
        if not board.buildSettle(player, settlement, start=True, verbose=verbose):
            raise Exception(f"Could not place SETTLEMENT at determined coordinates {settlement}")

        if not board.buildRoad(player, road, start=True, verbose=verbose): 
            raise Exception(f"Could not place ROAD at determined coordinates {road}")

        resources = {}
        for hex in BoardState.graph.intersections[settlement].hexes:
            resource = board.board[hex].produces(board.board[hex].number)
        if resource: resources[resource] = resources.get(resource, 0) + 1

        board.players[player].addResources(resources)
        if verbose:
            print ("Player %s starting with resources: %s" % (board.players[player].name, resources))

    for turn in range(0, 200):
        for pname in board.players:
            player = board.players[pname]
            bot = bots[pname]

            if verbose:
                print ("Turn %d Player %s" % (turn, player.name))
            # Play any Development Cards
            bot.playCards(player, board)

            # Produce
            # Pick a random spot for the robber to move if a 7 is rolled
            robber_opponent, robber_hex = bot.pickRobber(pname, board)
            board.produce(pname, robber_opponent, robber_hex, verbose=verbose)

            # Build
            if not bot.attemptBuild(player, board, verbose=verbose):
                # Trade
                choices = [x for x in D.RESOURCE_TYPES if player.canTrade(x)]
                if choices:
                    outgoing = random.choice(choices)
                    incoming = random.choice([x for x in D.RESOURCE_TYPES if x is not outgoing])
                    board.tradeMaritime(player.name, outgoing, incoming, verbose=verbose)

            if verbose:
                print (board.strPlayers())
            if player.victory == 10:
                if verbose:
                    print ("VICTORY for %s" % player.name)
                return player.name
        
    return "none"

bots = { "Red" : ModelBot.ModelBot("nightly_model_0.keras"), "Blue" : RandoBot.RandoBot(), "Yellow" : RandoBot.RandoBot(), "White" : RandoBot.RandoBot() }

start_time = time.time()
winners = {}
for _ in range(10000):
    winner = playGame(bots, verbose=False)
    winners[winner] = winners.get(winner, 0) + 1
print ("Elapsed Time:", str(time.time() - start_time))
print (winners)