# Ignore this file.  It didn't work out, but there is some good code so I don't want to delete it.
from BoardState import BoardState
import Defines as D

ACTION_OFFSET = 0 # 5 potential actions (5 values)
DEVELOPMENT_OFFSET = 5 # 9 Development Cards (9 values)
PATH_TARGET_OFFSET = 14 # 2 Road Targets (6 values)
RESOURCE_OFFSET = 20 # 2 Specified resources (2 values)
INTERSECTION_TARGET_OFFSET = 22 # 1 Specified intersection (3 values)
ROBBER_TARGET_OFFSET = 25 # 1 target of the robber (3 values)

_players = ["Red", "Blue", "Yellow", "Green"]
_board = BoardState(_players)

def act(pname, input):
    if input[0]:
        # play development card
        base = DEVELOPMENT_OFFSET
        card = None
        for i in range(0, len(D.DEVELOPMENT_CARDS)):
            if input[base + i]:
                card = D.DEVELOPMENT_CARDS[i]
                break
        if not card: return False

        extras = []
        if card is "Knight":
            base = ROBBER_TARGET_OFFSET
            extras.append(_reversePlayerIndex(pname, input[base])) # Robber target
            extras.append((input[base + 1], input[base + 2])) # Robber destination
        elif card is "Road Building":
            base = PATH_TARGET_OFFSET
            extras.extend([input[base], input[base + 1], input[base + 2]]) # two road destinations
            extras.extend([input[base + 3], input[base + 4], input[base + 5]]) # two road destinations
        elif card is "Monopoly":
            extras.append(D.RESOURCE_TYPES[input[RESOURCE_OFFSET]])
        elif card is "Year of Plenty":
            extras.extend([D.RESOURCE_TYPES[input[RESOURCE_OFFSET]], D.RESOURCE_TYPES[input[RESOURCE_OFFSET + 1]]])

        return _board.playDevelopment(pname, card, extras)
    elif input[1]:
        # Buy Development
        return _board.buyDevelopment(pname)
    elif input[2]:
        # Buy Road
        base = PATH_TARGET_OFFSET
        return _board.buildRoad(pname, (input[base], input[base + 1], input[base + 2]))
    elif input[3]:
        # Buy Settlement
        base = INTERSECTION_TARGET_OFFSET
        return _board.buildSettle(pname, (input[base], input[base + 1], input[base + 2]))
    elif input[4]:
        # Buy City
        base = INTERSECTION_TARGET_OFFSET
        return _board.buildCity(pname (input[base], input[base + 1], input[base + 2]))
    elif input[5]:
        # Trade Maritime
        base = RESOURCE_OFFSET
        return _board.tradeMaritime(pname, [D.RESOURCE_TYPES[input[base]]], [D.RESOURCE_TYPES[input[base + 1]]])

    return False

def boardState(pname):
    bs = []
    # static hex information
    N = 2
    sortedHexes = sorted(_board.board)
    for hex in sortedHexes:
            bs.append(D.tileIndex(_board.board[hex].tile))
            bs.append(_board.board[hex].number)
            bs.append(int(_board.board[hex].robber))
    for intersection in BoardState.graph.sortedIntersections:
        (p, v) = _intersectionType(intersection, _board.settlements, _board.cities)
        bs.append(_playerIndex(pname, p))
        bs.append(v)
    for path in BoardState.graph.sortedPaths:
        bs.append(_playerIndex(pname, _board.roads.get(path)))
    bs.append(len(_board.developments))

    _addPlayer(bs, pname)
    for player in [p for p in _board.players if p is not pname]:
        _addPlayer(bs, player)

    bs.append(_playerIndex(_board.longestRoad))
    bs.append(_playerIndex(_board.largestArmy))

    return bs

def parseState(bs, pname):
    print (bs)
    otherPlayers = [p for p in _board.players if p is not pname]

    base = 0
    for i in range(0, 19):
        print ("Tile Type: %s\tNumber: %d\tRobber: %s" % (D.TILE_TYPES[bs[base]], bs[base + 1], bool(bs[base + 2])))
        base += 3

    out = "Intersections:\n"
    count = 1
    for i in BoardState.graph.sortedIntersections:
        out += "\t%11s %s %s" % (i, _reversePlayerIndex(pname, bs[base]), _reverseIntersectionType(bs[base + 1]))
        if (count % 4 == 0): out += "\n"
        count += 1
        base += 2
    print (out + "\n")

    out = "Roads:\n"
    count = 1
    for i in BoardState.graph.sortedPaths:
        out += "\t%11s %s" % (i, _reversePlayerIndex(pname, bs[base]))
        if count % 5 == 0: out += "\n"
        count += 1
        base += 1
    print (out + "\n")

    print ("Developments Left:", bs[base])
    base += 1

    print ("Player:", pname)
    base += _parsePlayer(bs[base:])
    for i in range(0, len(otherPlayers)):
        print ("Player:", otherPlayers[i])
        base += _parsePlayer(bs[base:])

    print ("Longest Road: ", _reversePlayerIndex(pname, bs[base]))
    print ("Largest Army: ", _reversePlayerIndex(pname, bs[base + 1]))

def _addPlayer(bs, pname):
    player = _board.players[pname]
    bs.extend(player.resources)
    bs.append(player.victory)
    bs.append(player.military)
    bs.extend(player.supply)
    for card in D.DEVELOPMENT_CARDS:
        bs.append(sum(1 for c in player.developments if c == card))

def _parsePlayer(bs):
    print ("  Resources:", ", ".join(["%d %s" % (bs[D.resourceIndex(x)], x) for x in D.RESOURCE_TYPES]))
    print ("  Victory: %d\tMilitary: %d" % (bs[5], bs[6]))
    print ("  Supply: %d Roads, %d Settlments, %d Cities" % (bs[7], bs[8], bs[9]))
    output = "  Development Cards: "
    cards = []
    for i in range(0, len(D.DEVELOPMENT_CARDS)):
        if bs[10 + i] > 0:
            cards.append("%s: %d" % (D.DEVELOPMENT_CARDS[i], bs[10 + i]))
    if not cards: print (output + "None")
    else: print (output + ", ".join(cards))
    return 19
    

# Finds the player index of an player for a player
def _playerIndex(x, y):
    if y == None: return 0
    if x == y: return 1
    return [p for p in _players if p != x].index(y) + 1

def _reversePlayerIndex(x, y):
    if y == 0: return "None"
    if y == 1: return x
    return [p for p in _players if p != x][y - 1]

def _intersectionType(intersection, settlements, cities):
    if intersection in settlements: return (settlements[intersection], 1)
    if intersection in cities: return (settlements[intersection], 2)
    return (None, 0)

def _reverseIntersectionType(x):
    if x == 0: return "None"
    if x == 1: return "Settlement"
    if x == 2: return "City"

bs = boardState("Red")
parseState(bs, "Red")
