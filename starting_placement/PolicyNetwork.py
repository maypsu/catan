import numpy as np
import keras
import tensorflow as tf

@keras.saving.register_keras_serializable()
class PolicyNetwork(tf.keras.Model):
    def __init__(self, num_intersection, num_paths):
        super(PolicyNetwork, self).__init__()
        
        self.num_intersection = num_intersection
        self.num_paths = num_paths

        # Input layers
        self.hex_layer = tf.keras.layers.Dense(64, activation='relu')
        self.intersection_layer = tf.keras.layers.Dense(32, activation='relu')
        self.path_layer = tf.keras.layers.Dense(32, activation='relu')

        self.combine_layer = tf.keras.layers.Dense(128, activation='relu')

        # Output heads
        self.intersection_head = tf.keras.layers.Dense(num_intersection, activation='softmax')
        self.path_head = tf.keras.layers.Dense(num_paths, activation='softmax')

    def call(self, state):
        hex_features, intersection_features, path_features = state

        hex_output = self.hex_layer(hex_features)
        intersection_output = self.intersection_layer(intersection_features)
        path_output = self.path_layer(path_features)

        combined = tf.concat([hex_output, intersection_output, path_output], axis=-1)
        combined_output = self.combine_layer(combined)

        intersection_probs = self.intersection_head(combined_output)
        path_probs = self.path_head(combined_output)
        return intersection_probs, path_probs

    def get_config(self):
        base = super().get_config()

        config = { "num_intersection" : self.num_intersection, "num_paths" : self.num_paths }

        return {**base, **config}
    
    @classmethod
    def from_config(cls, config):
        num_intersection = config.pop("num_intersection")
        num_paths = config.pop("num_paths")

        return cls(num_intersection, num_paths)
    
    def argmax(self, state, valid_pairs, verbose=False):
        intersection_probs, path_probs = self(expand_dims(state))

        pair_indices, pair_probs = mask_and_sample(intersection_probs, path_probs, valid_pairs)
        if verbose:
            print ("ARGMAX: ")
            for i in range(len(pair_indices)):
                print(f"\t{pair_indices[i]} : {pair_probs[i]}")

        return pair_indices[np.argmax(pair_probs)]

def expand_dims(state):
    board_state, intersection_state, path_state = state
    return np.expand_dims(board_state, axis=0), np.expand_dims(intersection_state, axis=0), np.expand_dims(path_state, axis=0)

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
