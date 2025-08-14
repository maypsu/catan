import numpy as np
import random
import tensorflow as tf

from BoardState import BoardState
import visualization

from .PolicyNetwork import PolicyNetwork
from .TrainingEnvironment import TrainingEnvironment
from .dumbUtils import DumbBot

if __name__ == "__main__":
    model = tf.keras.models.load_model("training_model_1.keras")

    rewards = []
    for _ in range(1000):
        players = ["Red", "Blue", "Yellow", "White"]
        random.shuffle(players)
        env = TrainingEnvironment(BoardState(players), players, DumbBot())

        state = env.state()
        done =  False
        while not done:
            action = model.argmax(state, env.board.computeValidIntersectionPathPairs())
            state, reward, done = env.step(action)

        rewards.append(env.reward("Red"))

    print (np.min(rewards), np.max(rewards), np.mean(rewards))