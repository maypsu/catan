import argparse
import numpy as np
import random
import tensorflow as tf
import time

from BoardState import BoardState
import Defines as D
import visualization

from .PolicyNetwork import PolicyNetwork, mask_and_sample, expand_dims
from .TrainingEnvironment import TrainingEnvironment
from .RandoBot import RandoBot

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str, default="default.keras")
    parser.add_argument("--time", type=float, default=1)
    parser.add_argument("--fresh", action="store_false")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArguments()

    if args.fresh:
        model = PolicyNetwork(54, 72)
    else:
        if not args.input:
            raise Exception("Must specify --fresh or --input model")
        model = tf.keras.models.load_model(args.input)

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01) 
    start_time = time.time()

    iterations = 0
    while (time.time() - start_time) < args.time * 60:
        players = ["Red", "Blue", "Yellow", "Green"]
        random.shuffle(players)
        env = TrainingEnvironment(BoardState(players), players, RandoBot())

        with tf.GradientTape() as tape:
            logp = 0

            state = env.state()
            actions = []
            done = False
            while not done:
                intersection_probs, path_probs = model(expand_dims(state))

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
        iterations += 1

    model.save(args.output)
    print ("Elapsed Time: ", str(time.time() - start_time), "Iterations:", iterations, flush=True)
    visualization.draw_board(env.board, env.reward("Red"))