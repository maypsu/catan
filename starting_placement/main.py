import numpy as np
import tensorflow as tf
import random

from BoardState import BoardState
import Defines as D
import visualization

class TrainingEnvironment:
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.turns = players + list(reversed(players))
        self._simulatePlayers()

    def _simulatePlayers(self):
        while len(self.turns) > 0:
            next = self.turns.pop(0)
            if (next == "Red"):
                return False

            initialPlace(self.board.players[next], self.board)
        return True

    def state(self):
        board = self.board
        state = []
        players = [0] * len(self.players)
        players[self.players.index("Red")] = 1

        sortedHexes = sorted(board.board)
        for hex in sortedHexes:
            # tile type
            tile = [0] * 6
            tile[D.tileIndex(board.board[hex].tile)] = 1
            # tile number
            number = board.board[hex].number / 12
            state.extend(tile + [number])

        for intersection in board.graph.sortedIntersections:
            settled = [0] * len(self.players)
            if intersection in board.settlements:
                pname = board.settlements[intersection]
                settled[self.players.index(pname)] = 1
            elif intersection in board.cities:
                pname = board.cities[intersection]
                settled[self.players.index(pname)] = 1
            state.extend(settled)

        for path in board.graph.sortedPaths:
            settled = [0] * len(self.players)
            if path in board.roads:
                pname = board.roads[path]
                settled[self.players.index(pname)] = 1
            state.extend(settled)

        return np.array(state, dtype=np.float32)

    def step(self, action):
        intersection, path = action
        coordinate = self.board.graph.sortedIntersections[intersection].hexCoords[0]
        self.board.buildSettle("Red", coordinate, start=True, verbose=False)
        road = self.board.graph.sortedPaths[path].hexCoords[0]
        self.board.buildRoad("Red", road, start=True, verbose=False)
        
        done = self._simulatePlayers()
        reward = 0 if not done else self.reward()

        return self.state(), reward, done

    def reward(self):
        resources = []
        score = 0

        # Actual Victory Points
        #score = 2 # initial phase

        # Score for Partial Victory Points
        # resourcePropababilities = board.

        # Score for picking good numbers
        for _, intersection in self.board.graph.intersections.items():
            if intersection in self.board.settlements and self.board.settlements[intersection] == "Red":
                for hexCoord in intersection.hexes:
                    hex = self.board.board[hexCoord]  
                    probability = D.ODDS.get(hex.number, 0)
                    score += probability

                    # Harbor bonus (very small)
                    score += 0.05 if hexCoord in D.HARBORS else 0

                    resources.append(D.RESOURCE_PRODUCTION[hex.tile])

        score += len(set(resources)) / 2

        return score

class PolicyNetwork(tf.keras.Model):
    def __init__(self, num_vertices, num_paths):
        super(PolicyNetwork, self).__init__()
        
        # Shared layers
        self.shared_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(128, activation='relu'),
        ])
        
        # Output heads
        self.intersection_head = tf.keras.layers.Dense(num_vertices, activation='softmax')
        self.path_head = tf.keras.layers.Dense(num_paths, activation='softmax')

    def call(self, state):
        """
        Input: state tensor of shape [batch_size, state_dim]
        Output: 
            - intersection_probs: shape [batch_size, num_vertices]
            - path_probs: shape [batch_size, num_paths]
        """
        x = self.shared_layers(state)
        intersection_probs = self.intersection_head(x)
        path_probs = self.path_head(x)
        return intersection_probs, path_probs

def mask_and_sample(intersection_probs, path_probs, valid_pairs):
    """
    Given model outputs and a list of valid (intersection, path) pairs,
    compute masked joint probabilities over valid actions.
    """
    intersection_probs = intersection_probs.numpy().flatten()
    path_probs = path_probs.numpy().flatten()

    pair_indices = []
    pair_joint_probs = []

    for (i, j) in valid_pairs:
        prob = intersection_probs[i] * path_probs[j]
        pair_indices.append((i, j))
        pair_joint_probs.append(prob)

    pair_joint_probs = np.array(pair_joint_probs)

    if pair_joint_probs.sum() == 0:
        # Handle degenerate case where all probs are masked out
        # Default to uniform sampling
        pair_joint_probs = np.ones_like(pair_joint_probs) / len(pair_joint_probs)
    else:
        pair_joint_probs /= pair_joint_probs.sum()

    return pair_indices, pair_joint_probs

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

if __name__ == "__main__":
    model = PolicyNetwork(54, 72)
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)

    for _ in range(1000):
        players = ["Red", "Blue", "Yellow", "White"]
        random.shuffle(players)
        env = TrainingEnvironment(BoardState(players), players)

        with tf.GradientTape() as tape:
            logp = 0

            state = env.state()
            actions = []
            done = False
            while not done:
                state_tensor = tf.convert_to_tensor([state], dtype=tf.float32)
                intersection_probs, path_probs = model(state_tensor)

                valid_pairs = env.board.computeValidIntersectionPathPairs()
                pair_indices, pair_probs = mask_and_sample(intersection_probs, path_probs, valid_pairs)
                action_idx = np.random.choice(len(pair_indices), p=pair_probs)
                selected_action = pair_indices[action_idx]
                actions.append(selected_action)

                logp += tf.math.log(intersection_probs[0, selected_action[0]] + 1e-10) + tf.math.log(path_probs[0, selected_action[1]] + 1e-10)

                state, reward, done = env.step(selected_action)
            
            loss = -logp * reward

        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
    
    visualization.draw_board(env.board)