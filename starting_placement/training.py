import argparse
import numpy as np
import random
import tensorflow as tf
import time

from BoardState import BoardState

from .PolicyNetwork import PolicyNetwork, mask_and_sample, expand_dims
from .TrainingEnvironment import TrainingEnvironment
from bots.RandoBot import RandoBot
from bots.ModelBot import ModelBot

# This script is for training the learning model for the starting placement 
def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str) # the input model, if being used
    parser.add_argument("--output", type=str, default="default.keras") # the output model
    parser.add_argument("--time", type=float, default=1) # how long to spend training (min)
    parser.add_argument("--fresh", action="store_true") # use a fresh policy network instead of loading a model
    parser.add_argument("--random", action="store_true") # use RandoBot instead of ModelBot
    parser.add_argument("--segments", type=int, default=1) # allows multiple runs over a long period
    return parser.parse_args()

def run(model, bot, run_time, outfile):
    # Use the Adam optimizer
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01) 
    start_time = time.time()

    # For a period of time
    iterations = 0
    while (time.time() - start_time) < run_time * 60:
        # initialize a new enviornment
        players = ["Red", "Blue", "Yellow", "Green"]
        random.shuffle(players)
        env = TrainingEnvironment(BoardState(players), players, bot)

        with tf.GradientTape() as tape:
            logp = 0

            state = env.state()
            actions = []
            done = False
            # Two step process - first placement then second placement
            while not done:
                intersection_probs, path_probs = model(expand_dims(state))

                # Need to mask road placements, since the settlement placement decides the road placements
                valid_pairs = env.board.computeValidIntersectionPathPairs()
                pair_indices, pair_probs = mask_and_sample(intersection_probs, path_probs, valid_pairs)

                # Choose a reandom action
                action_idx = np.random.choice(len(pair_indices), p=pair_probs)
                selected_action = pair_indices[action_idx]
                actions.append(selected_action)

                # Math like crazy
                logp += tf.math.log(intersection_probs[0, selected_action[0]] + 1e-10) + tf.math.log(path_probs[0, selected_action[1]] + 1e-10)

                state, reward, done = env.step(selected_action)
            
            loss = -logp * reward

        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        iterations += 1

    model.save(outfile)
    print ("Elapsed Time: ", str(time.time() - start_time), "Iterations:", iterations, flush=True)

if __name__ == "__main__":
    args = parseArguments()

    if args.fresh:
        model = PolicyNetwork(54, 72)
    else:
        if not args.input: raise Exception("Must specify --fresh or --input model")
        model = tf.keras.models.load_model(args.input)

    if args.random:
        bot = RandoBot()
    else:
        if not args.input: raise Exception("Must specify --random or --input model")
        bot = ModelBot(args.input)

    for i in range(args.segments):
        outfile = args.output.format(i)
        run(model, bot, args.time, outfile)
