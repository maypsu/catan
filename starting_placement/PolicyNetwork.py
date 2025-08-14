import numpy as np
import keras
import tensorflow as tf

@keras.saving.register_keras_serializable()
class PolicyNetwork(tf.keras.Model):
    def __init__(self, num_vertices, num_paths):
        super(PolicyNetwork, self).__init__()
        
        self.num_vertices = num_vertices
        self.num_paths = num_paths

        # Shared layers
        self.shared_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(128, activation='relu'),
        ])
        
        # Output heads
        self.intersection_head = tf.keras.layers.Dense(num_vertices, activation='softmax')
        self.path_head = tf.keras.layers.Dense(num_paths, activation='softmax')

    def get_config(self):
        base = super().get_config()

        config = { "num_vertices" : self.num_vertices, "num_paths" : self.num_paths }

        return {**base, **config}
    
    @classmethod
    def from_config(cls, config):
        num_vertices = config.pop("num_vertices")
        num_paths = config.pop("num_paths")

        return cls(num_vertices, num_paths)

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
    
    def argmax(self, state, valid_pairs, verbose=False):
        state_tensor = tf.convert_to_tensor([state], dtype=tf.float32)
        intersection_probs, path_probs = self(state_tensor)

        pair_indices, pair_probs = mask_and_sample(intersection_probs, path_probs, valid_pairs)
        if verbose:
            print ("ARGMAX: ")
            for i in range(len(pair_indices)):
                print(f"\t{pair_indices[i]} : {pair_probs[i]}")

        return pair_indices[np.argmax(pair_probs)]

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
