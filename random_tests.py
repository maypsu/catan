import random

import BoardState
import starting_placement.BetterBot as BetterBot
import visualization


players = ["Red", "Blue", "Yellow", "Green"]
random.shuffle(players)
board = BoardState.BoardState(players)

board.buildSettle("Red", (0, 0, 0), start=True)
board.buildRoad("Red", (0, 0, 0), start=True)
board.buildSettle("Red", (2, -2, 2), start=True)
board.buildRoad("Red", (2, -2, 2), start=True)

board.buildSettle("Green", (1, -1, 1), start=True)
board.buildRoad("Green", (1, -1, 1), start=True)
board.buildSettle("Green", (0, 0, 4), start=True)
board.buildRoad("Green", (0, 0, 4), start=True)

board.buildSettle("Green", (2, -1, 5), start=True)
board.buildRoad("Green", (2, -1, 5), start=True)
board.buildSettle("Green", (2, -1, 3), start=True)
board.buildRoad("Green", (2, -1, 3), start=True)


bot = BetterBot.BetterBot()
road = bot.pickRoad("Red", board)
print (road if road else "None", flush=True)
board.buildRoad("Red", road.hexCoords[0], start=True, verbose=True)

visualization.draw_board(board, 0.0)