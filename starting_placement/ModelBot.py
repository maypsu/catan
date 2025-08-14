import numpy as np
import tensorflow as tf

from .PolicyNetwork import PolicyNetwork
from .RandoBot import RandoBot

class ModelBot(RandoBot):
    def __init__(self, filename):
        super().__init__()

        self.model = tf.keras.models.load_model(filename)

    def initialPlace(self, player, board):
        settlement, road = self.model.argmax(board.state(), board.computeValidIntersectionPathPairs())
        return board.graph.sortedIntersections[settlement].hexCoords[0], board.graph.sortedPaths[road].hexCoords[0]
