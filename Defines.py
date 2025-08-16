RESOURCE_TYPES = ["Brick", "Lumber", "Ore", "Grain", "Wool"]
BRICK = 0
LUMBER = 1
ORE = 2
GRAIN = 3
WOOL = 4

SUPPLY_TYPES = ["Road", "Settlement", "City", "Development"]
ROAD = 0
SETTLEMENT= 1
CITY = 2
DEVELOPMENT = 3

HARBOR_TYPES = ["Wild"] + RESOURCE_TYPES

TILE_TYPES = ["Hills", "Forest", "Mountains", "Fields", "Pasture", "Desert"]
HILLS = 0
FOREST = 1
MOUNTAIN = 2
FIELDS = 3
PASTURE = 4
DESERT = 5

VICTORY_CARDS= ["Great Hall", "University", "Chapel", "Market", "Library"]
DEVELOPMENT_CARDS = ["Knight", "Road Building", "Monopoly", "Year of Plenty"] + VICTORY_CARDS

SUPPLY_COSTS = { "Settlement" : {"Brick" : 1, "Lumber" : 1, "Wool" : 1, "Grain" : 1},
            "Road" : {"Brick" : 1, "Lumber" : 1},
            "City" : {"Ore" : 3, "Grain" : 2},
            "Development" : {"Ore" : 1, "Wool" : 1, "Grain" : 1} }

TILES = ["Desert"] + ["Fields"] * 4 + ["Pasture"] * 4 + ["Forest"] * 4 + ["Hills"] * 3 + ["Mountains"] * 3
NUMBERS = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
ODDS = {2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36}



HARBORS = { (0, -2, 0) : "Wild",   (0, -2, 1)  : "Wild", 
            (1, -2, 1) : "Grain",  (1, -2, 2)  : "Grain",  (2, -2, 0)  : "Grain",
            (2, -2, 3) : "Ore",    (2, -1, 1)  : "Ore",    (2, -1, 2)  : "Ore",
            (2, 0, 2)  : "Wild",   (2, 0, 3)   : "Wild",
            (1, 1, 3)  : "Wool",   (1, 1, 4)   : "Wool",   (0, 2, 2)   : "Wool",
            (-1, 2, 3) : "Wild",   (-1, 2, 4)  : "Wild",   (0, 2, 5)   : "Wild",
            (-2, 2, 4) : "Wild",   (-2, 2, 5)  : "Wild",
            (-2, 0, 4) : "Brick",  (-2, 1, 0)  : "Brick",  (-2, 1, 5)  : "Brick",
            (-2, 0, 1) : "Lumber", (-1, -1, 0) : "Lumber", (-1, -1, 5) : "Lumber" }

RESOURCE_PRODUCTION = {"Hills": "Brick", "Forest": "Lumber", "Mountains": "Ore", "Fields": "Grain", "Pasture": "Wool", "Desert" : None}

NUMBER_PLACEMENTS = [[(0, -2), (-1, -1), (-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 2), (1, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, -1), (0, 0)],
                     [(-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 2), (1, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (0, 0)],
                     [(-2, 2), (-1, 2), (0, 2), (1, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (-2, 0), (-2, 1), (-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (0, 0)],
                     [(0, 2), (1, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 0)],
                     [(2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -1), (-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 2), (1, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1), (0, 0)],
                     [(2, -2), (1, -2), (0, -2), (-1, -1), (-2, 0), (-2, 1), (-2, 2), (-1, 2), (0, 2), (1, 1), (2, 0), (2, -1), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (0, 0)]]

def supplyIndex(supply):
    return SUPPLY_TYPES.index(supply)

def supplyCost(supply):
    return SUPPLY_COSTS[supply]

def harborIndex(harbor):
    return HARBOR_TYPES.index(harbor)

def resourceIndex(resource):
    return RESOURCE_TYPES.index(resource)

def tileIndex(tile):
    return TILE_TYPES.index(tile)

def developmentIndex(dev):
    return DEVELOPMENT_CARDS.index(dev)

def canBuildCity(resources):
    return resources[ORE] >= 3 and resources[GRAIN] >= 2

def canBuildSettlement(resources):
    return resources[BRICK] >= 1 and resources[LUMBER] >= 1 and resources[GRAIN] >= 1 and resources[WOOL] >= 1

def canBuyDevelopmentCard(resources):
    return resources[ORE] >= 1 and resources[GRAIN] >= 1 and resources[WOOL] >= 1

def canBuildRoad(resources):
    return resources[LUMBER] >= 1 and resources[BRICK] >= 1