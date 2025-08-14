import numpy as np
import random
import tensorflow as tf

from BoardState import BoardState
import visualization

from .PolicyNetwork import PolicyNetwork
from .TrainingEnvironment import TrainingEnvironment

if __name__ == "__main__":
    model = tf.keras.models.load_model("testing_model.keras")

    players = ["Red", "Blue", "Yellow", "White"]
    random.shuffle(players)
    env = TrainingEnvironment(BoardState(players), players)

    state = env.state()

    done =  False
    while not done:
        action = model.argmax(state, env.board.computeValidIntersectionPathPairs())
        state, reward, done = env.step(action)

    print ("Final Score:", env.reward("Red"))
    visualization.draw_board(env.board)    
