class Graph:
    def __init__(self):
        self.intersections = {}
        self.paths = {}

        N = 2
        for q in range(-N, N + 1):
            for r in range(max(-N, -q - N), min(N, -q + N) + 1):
                for x in range(0, 6):
                    if (q, r, x) not in self.intersections:
                        inter = Intersection((q, r, x))
                        for hex in inter.hexCoords:
                            self.intersections[hex] = inter
                    if (q, r, x) not in self.paths:
                        path = Path((q, r, x))
                        for hex in path.hexCoords:
                            self.paths[hex] = path

        for inter in set(self.intersections.values()):
            for (q, r, x) in inter.hexCoords:
                # Clockwise
                path = self.paths[(q, r, x)]
                neighbor = self.intersections[(q, r, (x + 1) % 6)]
                inter.adjacent.add((path, neighbor))
                path.adjacent.update([inter, neighbor])

                # Counter-clockwise
                path = self.paths[(q, r, (x - 1) % 6)]
                neighbor = self.intersections[(q, r, (x - 1) % 6)]
                inter.adjacent.add((path, neighbor))
                path.adjacent.update([inter, neighbor])

        self.sortedIntersections = sorted(set(self.intersections.values()), key=lambda x: x.hexCoords[0])
        self.sortedPaths = sorted(set(self.paths.values()), key = lambda x: x.hexCoords[0])

class Intersection:
    def __init__(self, coordinate):
        self.hexCoords = sorted(expandIntersection(coordinate))
        self.hexes = set([(q, r) for (q, r, _) in self.hexCoords])
        self.adjacent = set()

    def canConnect(self, pname, roads):
        value = False
        for path in [x for (x, _) in self.adjacent]:
            if path in roads and roads[path] == pname:
                return True
        return False

    def blockedSettle(self, occupied):
        # Can only build if no one has built here yet
        if self in occupied:
            return True
 
        # Can't build if their are settlements on the neighboring intersections
        for inter in [x for (_, x) in self.adjacent]:
            if inter in occupied: return True

        return False
    
    def blockedCity(self, pname, settlements):
        return self not in settlements or settlements[self] is not pname

    def __eq__(self, other):
        if not isinstance(other, Intersection): return NotImplemented
        return self.hexCoords[0] == other.hexCoords[0]
    
    def __hash__(self):
        return self.hexCoords[0].__hash__()
    
    def __lt__(self, other):
        if not isinstance(other, Intersection): return NotImplemented
        return self.hexCoords[0] < other.hexCoords[0]

    def __str__(self):
        return str(self.hexCoords) #[0])

class Path:
    def __init__(self, coordinate):
        self.hexCoords = sorted(expandPath(coordinate))
        self.hexes = set([(q, r) for (q, r, _) in self.hexCoords])
        self.adjacent = set()

    def blockedRoad(self, roads):
        return self in roads

    def canConnect(self, pname, roads, settlements={}, start=False):
        for inter in self.adjacent:
            if start and settlements.get(inter) is pname: return True
            if not start:
                for path in [x for (x, _) in inter.adjacent]:
                    if roads.get(path) is pname: return True
        
        return False
    
    def __eq__(self, other):
        if not isinstance(other, Path): return NotImplemented
        return self.hexCoords[0] == other.hexCoords[0]
    
    def __hash__(self):
        return self.hexCoords[0].__hash__()
    
    def __lt__(self, other):
        if not isinstance(other, Path): return NotImplemented
        return self.hexCoords[0] < other.hexCoords[0]

    def __str__(self):
        return str(self.hexCoords) #[0])

def expandIntersection(intersection):
    (q, r, x) = intersection

    expanded = [(q, r, x)]
    s = -q - r
    # Join upper left
    if (x == 0 or x == 1) and r != -2 and s != 2:
        expanded.append((q, r - 1, 4 - x))
    # Join upper right
    if (x == 1 or x == 2) and r != -2 and q != 2:
        expanded.append((q + 1, r - 1, 6 - x))
    # Join right
    if (x == 2 or x == 3) and q != 2 and s != -2:
        expanded.append((q + 1, r, 0 if x == 2 else 5))
    # Join lower right
    if (x == 3 or x == 4) and r != 2 and s != -2:
        expanded.append((q, r + 1, 4 - x))
    # Join lower left
    if (x == 4 or x == 5) and r != 2 and q != -2:
        expanded.append((q - 1, r + 1, 6 - x))
    # Join left
    if (x == 5 or x == 0) and s != 2 and q != -2:
        expanded.append((q - 1 , r, 2 if x == 0 else 3))
    
    return expanded

def expandPath(path):
    (q, r, x) = path

    expanded = [(q, r, x)]
    s = -q - r
    # Join upper left
    if (x == 0) and r != -2 and s != 2:
        expanded.append((q, r - 1, 3))
    # Join upper right
    if (x == 1) and r != -2 and q != 2:
        expanded.append((q + 1, r - 1, 4))
    # Join right
    if (x == 2) and q != 2 and s != -2:
        expanded.append((q + 1, r, 5))
    # Join lower right
    if (x == 3) and r != 2 and s != -2:
        expanded.append((q, r + 1, 0))
    # Join lower left
    if (x == 4) and r != 2 and q != -2:
        expanded.append((q - 1, r + 1, 1))
    # Join left
    if (x == 5) and s != 2 and q != -2:
        expanded.append((q - 1 , r, 2))

    return expanded
