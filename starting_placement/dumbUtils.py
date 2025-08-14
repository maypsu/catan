import random

def pickRandom():
    while True:
        q = random.randint(-2, 2)
        r = random.randint(-2, 2)
        x = random.randint(0, 5)

        s = -q - r
        if s < -2 or s > 2:
            continue

        return (q, r, x)
    
def initialPlace(player, board):
    while True:
        coordinate = pickRandom()
        intersection = board.graph.intersections[coordinate]
        if intersection.blockedSettle(board.settlements | board.cities):
            continue

        foundPath = None
        for (path, _) in intersection.adjacent:
            if not path.blockedRoad(board.roads):
                foundPath = path
                break
        
        if not foundPath:
            continue

        if not board.buildSettle(player.name, coordinate, True, verbose=False): 
            raise Exception("Could not place settlement at determined coordinates")
    
        if not board.buildRoad(player.name, path.hexCoords[0], True, verbose=False): 
            raise Exception("Could not place path because there were no valid locations")
        
        break
    return