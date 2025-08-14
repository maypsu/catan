import numpy as np
import tensorflow as tf
import keras
import random

from BoardState import BoardState
import Defines as D
import visualization

from .PolicyNetwork import PolicyNetwork, mask_and_sample
from .TrainingEnvironment import TrainingEnvironment


if __name__ == "__main__":
    #model = PolicyNetwork(54, 72)
    model = tf.keras.models.load_model("testing_model.keras")
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

    model.save("testing_model2.keras")
    print ("Final score:", env.reward("Red"))
    visualization.draw_board(env.board)