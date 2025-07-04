from BoardState import BoardState
import Defines as D
import IntersectionGraph as IG
import random

pnames = ["Red", "Blue", "Yellow", "White"]
board = BoardState(pnames)

def pickRandom():
    while True:
        q = random.randint(-2, 2)
        r = random.randint(-2, 2)
        x = random.randint(0, 5)

        s = -q - r
        if s < -2 or s > 2:
            continue

        return (q, r, x)

def initialPlace(player):
    settles = 0
    q = 0
    r = 0
    x = 0
    while True:
        settles += 1
        coordinate = pickRandom()
        if board.buildSettle(player.name, coordinate, True): 
            print ("Settlement: %s %s" % (player.name, coordinate), flush=True)
            break

    roads = 0
    intersection = BoardState.graph.intersections[coordinate]
    paths = [x for (x, _) in intersection.adjacent]
    random.shuffle(paths)
    path = paths.pop()
    while path:    
        if path.canConnect(player.name, board.roads, board.settlements, True) and not path.blockedRoad(board.roads): break
        path = paths.pop()
    
    if not path or not board.buildRoad(player.name, path.hexCoords[0], True): 
        raise Exception("Could not place path because there were no valid locations")
    
    resources = {}
    for hex in BoardState.graph.intersections[coordinate].hexes:
        resource = board.board[hex].produces(board.board[hex].number)
        if resource: resources[resource] = resources.get(resource, 0) + 1

    print ("Player %s picked in %d settle and %d road attempts" % (player.name, settles, roads))
    return resources

statistics = [0, 0, 0, 0]
def attemptBuild(player):
    pname = player.name
    if (player.canAffordResources(D.supplyCost("City")) and player.supply[2] > 0 and player.supply[1] < 5):
        for _ in range(0, 100):
            if board.buildCity(pname, pickRandom()):
                statistics[2] += 1
                return True

    if (player.canAffordResources(D.supplyCost("Settlement")) and player.supply[1] > 0):
        for _ in range(0, 100):
            if board.buildSettle(pname, pickRandom()):
                statistics[1] += 1
                return True

    if (player.canAffordResources(D.supplyCost("Road")) and player.supply[0] > 0):
        for _ in range(0, 100):
            if board.buildRoad(pname, pickRandom()):
                statistics[0] += 1
                return True

    if (player.canAffordResources(D.supplyCost("Development")) and board.developments):
        board.buyDevelopment(pname)
        statistics[3] += 1
        return True
    
    return False
    
def randomRobber(pname):
    while True:
        (q, r, _) = pickRandom()
        robber = (q, r)

        producers = board.settlements | board.cities
        for x in range(0, 6):
            intersection = BoardState.graph.intersections[(q, r, x)]
            if intersection in producers and producers[intersection] is not pname: 
                return [producers[intersection], robber]

def randomRoad(pname, start):
    while True:
        coordinate = pickRandom()
        path = BoardState.graph.paths[coordinate]
        if path.canConnect(pname, board.roads, board.settlements, start):
            return coordinate

def randomExtra(card, pname):
    if card in D.VICTORY_CARDS:
        return []
    if card == "Knight":
        return randomRobber(pname)
    if card == "Road Building":
        return [randomRoad(pname, False), randomRoad(pname, False)]
    if card == "Monopoly":
        return random.choices(D.RESOURCE_TYPES, k=1)
    if card == "Year of Plenty":
        return random.choices(D.RESOURCE_TYPES, k=2)

for player in board.players:
    initialPlace(board.players[player])

for player in reversed(board.players):
    resources = initialPlace(board.players[player])
    board.players[player].addResources(resources)
    print ("Player %s starting with resources: %s" % (board.players[player].name, resources))

print (str(board))

def _main():
    for turn in range(0, 100):
        for pname in board.players:
            player = board.players[pname]
            print ("Turn %d Player %s" % (turn, player.name))
            if (player.developments):
                card = random.choice(player.developments)
                ds = 0
                for _ in range(0, 100):
                    ds += 1
                    if board.playDevelopment(player.name, card, randomExtra(card, player.name)):
                        break

            # Produce
            # Pick a random spot for the robber to move
            robber = randomRobber(pname)
            board.produce(pname, robber[0], robber[1])

            # Build
            if not attemptBuild(player):
                # Trade
                choices = [x for x in D.RESOURCE_TYPES if player.canTrade(x)]
                if choices:
                    outgoing = random.choice(choices)
                    incoming = random.choice([x for x in D.RESOURCE_TYPES if x is not outgoing])
                    board.tradeMaritime(player.name, outgoing, incoming)

            print (board.strPlayers())
            if player.victory == 10:
                print ("VICTORY for %s" % player.name)
                return

# try:
_main()
# except Exception as ex:
#     print (ex)

print (str(board))
print (str(statistics))
