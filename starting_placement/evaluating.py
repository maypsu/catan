import argparse
import numpy as np
import random
import tensorflow as tf

from BoardState import BoardState
import visualization

from .PolicyNetwork import PolicyNetwork
from .TrainingEnvironment import TrainingEnvironment
from .RandoBot import RandoBot

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    return parser.parse_args()


if __name__ == "__main__":
    args = parseArguments()
    model = tf.keras.models.load_model(args.input)

    rewards = []
    for _ in range(1):
        # print ("=========================")
        players = ["Red", "Blue", "Yellow", "Green"]
        random.shuffle(players)
        env = TrainingEnvironment(BoardState(players), players, RandoBot())

        state = env.state()
        done =  False
        while not done:
            action = model.argmax(state, env.board.computeValidIntersectionPathPairs(), verbose=False)

            print ("Action: ", env.board.graph.sortedIntersections[action[0]], env.board.graph.sortedPaths[action[1]])
            state, reward, done = env.step(action, verbose=True)

        rewards.append(reward)
        print(env.board.__str__())
        print ("flush", flush=True)
        visualization.draw_board(env.board, env.reward("Red"))

    print (np.min(rewards), np.max(rewards), np.mean(rewards))