import random
import Defines as D
# Decision Tree for which cards to trade

# The resources required to build one of something
BASE_RESOURCES = [1, 1, 3, 2, 1]

# Execute the tree to decide what trades to offer
def getTrades(pname, board):
    player = board.players[pname]
    resources = player.resources.copy()

    # Can I currently build?
    if canBuildAny(resources):
        return []

    # Do I have anything to trade
    extras = [max(0, x - y) for x, y in zip(resources, BASE_RESOURCES)]
    if not any(count > 0 for count in extras):
        return []
    
    # Does anyone have what I'm missing
    player_missing = []
    for target in [D.SETTLEMENT, D.CITY, D.DEVELOPMENT, D.ROAD]:
        m = missingResources(resources, target)
        if any(count > 0 for count in m):
            player_missing.append((target, m))
    if not player_missing: return []

    possible_trades = []
    for opponent in board.players.values():
        if opponent.name is not pname:
            opponent_extras = [max(0, x - y) for x, y in zip(opponent.resources, BASE_RESOURCES)]
            if not any(count > 0 for count in opponent_extras): continue
            for pm in player_missing:
                overlap = [x - y for x, y in zip(opponent_extras, pm[1])]
                if all(count >= 0 for count in  overlap):
                    possible_trades.append((opponent, pm))
    if not possible_trades: return []

    # Would the trade help the opponent more? (i.e. don't give them a settlment/city if we're not getting one)
    acceptable_trades = []
    for trade in possible_trades:
        (opponent, (target, miss)) = trade
        give, take = fairTrade(extras, miss)

        # We're getting a settlement/city or they already can build one, so don't worry about it 
        if target == D.SETTLEMENT or target == D.CITY or D.canBuildSettlement(opponent.resources) or D.canBuildCity(opponent.resources):
            acceptable_trades.append((opponent, give, take))
            continue

        _, new_opponent = performTrade(resources, opponent.resources, give, take)

        # Reject that.
        if not D.canBuildSettlement(new_opponent) and not D.canBuildCity(new_opponent):
            acceptable_trades.append((opponent, give, take))

    return acceptable_trades

# Consider whether to accept a trade
def considerTrade(player, opponent, give, take):
    player_resources = player.resources

    # Do I have any extra resources?
    extras = [max(0, x - y) for x, y in zip(player_resources, BASE_RESOURCES)]
    if not all([count > 0 for count in extras]): return False

    # Is the trade balanced or in my favor?
    if sum(give) < sum(take): return False

    # Do I have what they're asking
    remainders = [x - y for x, y in zip(extras, give)]
    if any(count < 0 for count in remainders): return False

    # Evaluate the trade
    new_player, new_opponent = performTrade(player_resources, opponent.resources, give, take)

    # Will this trade allow the opponent to build something I care about?
    if (not D.canBuildSettlement(opponent.resources) and D.canBuildSettlement(new_opponent)) \
        or (not D.canBuildCity(opponent.resources) and D.canBuildCity(new_opponent)):
        # Will this trade let me build anything I care about?
        if (not D.canBuildSettlement(player_resources) and D.canBuildSettlement(new_player)) \
            or (not D.canBuildCity(player_resources) and D.canBuildCity(new_player)):
            return True
        return False    
    
    # Okay fam, lets play
    return True

# Can the resources build anything?
def canBuildAny(resources):
    return D.canBuildCity(resources) or D.canBuildSettlement(resources) or D.canBuyDevelopmentCard(resources)

# What resources are missing to build the target building type?
def missingResources(resources, target):
    missing = [0] * 5
    for resource, cost in D.SUPPLY_COSTS[D.SUPPLY_TYPES[target]].items():
        index = D.resourceIndex(resource)
        if resources[index] < cost:
            missing[index] = cost - resources[index]
    return missing

# simulate trading the resources
def performTrade(player_resources, opponent_resources, give, take):
    return [x - g + t for x, g, t in zip(player_resources, give, take)], [x + g - t for x, g, t in zip(opponent_resources, give, take)]

# compute a fair trade by equalizing the resources
def fairTrade(extras, miss):
    miss_count = sum(miss)
    extra_count = sum(extras)
    if miss_count == extra_count:
        return extras, miss

    if miss_count < extra_count:
        e = extras.copy()
        for _ in range(extra_count - miss_count):
            options = [x for x in e if x > 0]
            selection = random.choice(options)
            i = e.index(selection)
            e[i] -= 1
        return e, miss
    else:
        m = miss.copy()
        for _ in range(miss_count - extra_count):
            options = [x for x in m if x > 0]
            selection = random.choice(options)
            i = m.index(selection)
            m[i] -= 1
        return extras, m

# Test?  TEST!!
if __name__ == "__main__":
    from BoardState import BoardState
    players = ["Red", "Blue", "Yellow", "Green"]
    random.shuffle(players)
    board = BoardState(players)

    player_one = board.players["Red"]
    player_one.resources[0] = 1
    player_one.resources[1] = 1
    player_one.resources[2] = 2
    player_one.resources[3] = 2
    player_one.resources[4] = 0

    player_two = board.players["Blue"]
    player_two.resources[3] = 1
    player_two.resources[4] = 1

    trade = offerTrade("Red", board)
    print (f"{trade}")

    print (considerTrade("Blue", board, (1, "Brick"), (1, "Wool")))
