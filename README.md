# Settlers of Catan

## Key Classes
### Board State
This class represents the state of the game.  It manages almost all of the state maintenance in the framework.

### starting_placement.training
This is the main script for training the starting placement model.

### starting_placement.PolicyNetwork
Implementation of the starting placement learning model.

### starting_placement.TrainingEnvironment
The step function and reward function for training the starting_placement 

### RobberMCTS
Implements the monte-carlo tree search for choosing where to place the Robber token

### TradeCards
Decision tree to decide what cards to trade, and whether to accept a trade

### visualization
Visualize the board in a window