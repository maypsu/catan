import random
import math
from collections import defaultdict

from BoardState import BoardState
import visualization

# Run the MCTS for choosing where the Robber token should be placed
def mctsRobber(pname, board):
    root = build_tree("Red", board)
    run_mcts(pname, board, root, iterations=100)
    best_child = max(root.children, key=lambda c: c.total_reward / c.visits if c.visits > 0 else float('-inf'))

    return best_child.move

# Node class for MCTS
class Node:
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0.0

# Upper Confidence Bound formula for child selection (pg. 585)
def ucb(parent_visits, child_visits, child_total_reward, exploration=1.41):
    if child_visits == 0:
        return float('inf')
    return (child_total_reward / child_visits) + exploration * math.sqrt(math.log(parent_visits) / child_visits)

# Select child using UCB
def select_child(node):
    return max(node.children, key=lambda c: ucb(node.visits, c.visits, c.total_reward))

# Simulate dice roll (2d6)
def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)

# Simulation: Estimate reward for a move by simulating random dice rolls over num_turns
# Reward = self's gains (including steal) - max opponent's gains
# Assumes all settlements (1 resource per production), ignores resource types, no further moves
def simulate(pname, board, move, num_turns=20):
    blocked_hex, victim = move
    
    # Initial steal: self gains 1, victim loses 1 (applied later)
    self_gains = 1.0
    
    # Gains per player from production
    opponent_gains = defaultdict(float)
    
    for _ in range(num_turns):
        roll = roll_dice()
        if roll == 7:
            continue  # Ignore 7s in simulation (no additional robber moves)
        
        for coords, hex in board.board.items():
            if hex.number == roll and hex != blocked_hex:
                for settlement, player in board.settlements.items():
                    if hex.coords in settlement.hexes:
                        if player == pname:
                            self_gains += 1
                        else:
                            opponent_gains[victim] += 1
                for city, player in board.cities.items():
                    if hex.coords in city.hexes:
                        if player == pname:
                            self_gains += 2
                        else:
                            opponent_gains[victim] += 2                    
    
    # Apply steal to victim
    opponent_gains[victim] -= 1
    
    # Reward: self_gains - max_opponent_gains
    max_opp = max(opponent_gains.values()) if opponent_gains else 0
    reward = self_gains - max_opp
    return reward

# Run MCTS
def run_mcts(pname, board, root, iterations=100):
    for _ in range(iterations):
        child = select_child(root)
        reward = simulate(pname, board, child.move)
        child.total_reward += reward
        child.visits += 1
        root.visits += 1

def build_tree(pname, board, verbose=False):
    moves = []
    # Generate possible moves: (hex, victim)
    for intersection, v in board.settlements.items():
        if v is not pname:
            for hex in [board.board[h] for h in intersection.hexes]:
                moves.append((hex, v))

    for intersection, v in board.cities.items():
        if v is not pname:
            for hex in [board.board[h] for h in intersection.hexes]:
                moves.append((hex, v))

    if verbose:
        print (f"Possible moves: {moves}", flush=True)

    # Main execution
    root = Node()  # Root node (no move)

    # Expand root with all possible moves
    for m in moves:
        root.children.append(Node(m, root))
    
    return root

if __name__ == "__main__":
    players = ["Red", "Blue", "Yellow", "Green"]
    random.shuffle(players) 
    board = BoardState(players)
    board.buildSettle("Blue", (0, 0, 0), start=True)
    board.buildSettle("Yellow", (1, -1, 3), start=True)
    board.buildSettle("Green", (1, 1, 5), start=True)
    board.buildSettle("Red", (0, -1, 2), start=True)

    root = build_tree("Red", board, verbose=True)

    # Run MCTS simulations
    run_mcts("Red", board, root)

    # Select best move (highest average reward)
    best_child = max(root.children, key=lambda c: c.total_reward / c.visits if c.visits > 0 else float('-inf'))
    best_move = best_child.move
    best_avg_reward = best_child.total_reward / best_child.visits if best_child.visits > 0 else 0

    print(f"Best move: Place robber on hex {best_move[0]} and steal from player {best_move[1]}")
    print(f"Average reward: {best_avg_reward:.2f}")
    print(f"Visits for best move: {best_child.visits}", flush=True)
    visualization.draw_board(board, 0.0)