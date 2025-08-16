import argparse
import random
import time

from BoardState import BoardState
import Defines as D
import IntersectionGraph as IG
import starting_placement.RandoBot as RandoBot
import starting_placement.ModelBot as ModelBot
import visualization

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="fooling.keras", type=str)
    parser.add_argument("--range", default=10000, type=int)
    parser.add_argument("--visualize", action="store_true")
    return parser.parse_args()

def playGame(bots, verbose=True):

    players = ["Red", "Blue", "Yellow", "Green"]
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
            bot.playCards(player, board, verbose=verbose)

            # Produce
            # Pass the player bot to pick a random spot for the robber to move if a 7 is rolled
            board.produce(pname, bot, verbose=verbose)

            # Trades!
            trades = bot.getTrades(pname, board)
            if trades:
                accepts = []
                for (opponent, give, take) in trades:
                    if bots[opponent.name].considerTrade(opponent, player, take, give):
                        try:
                            board.executeTrade(player, opponent, give, take)
                        except Exception:
                            print (f"Player: {player}")
                            print (f"Opponent: {opponent}")
                            print (f"Give: {give} Take: {take}")
                            raise
                        break

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
                return player.name, board
        
    return "none", board

args = parseArguments()
bots = { "Red" : ModelBot.ModelBot(args.input), "Blue" : RandoBot.RandoBot(), "Yellow" : RandoBot.RandoBot(), "Green" : RandoBot.RandoBot() }

start_time = time.time()
winners = {}
for _ in range(args.range):
    winner, board = playGame(bots, verbose=False)
    winners[winner] = winners.get(winner, 0) + 1
print ("Elapsed Time:", str(time.time() - start_time))
print (winners)

if args.visualize: visualization.draw_board(board, 0.0)