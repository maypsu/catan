# Settlers of Catan

## To run the programs

### Score a starting placement model against the reward function
python -m score_stats --input saved_models/candidate_2.keras

### Run the simulation to compare performance of the model bot
python -m run --input saved_models/candidate_2.keras

### Run the simulation to compare performance of the heuristic bot
python -m run --better

### To train a new version of the starting placement bot
python -m starting_placement.training --fresh --random --time 10 --output 'trial_{}.out'

This will generate a model in the file 'trial_1.out' using a fresh policy network and the RandoBot to train.  It will run for 10 minutes.

## Key Classes
### Board State
This class represents the state of the game.  It manages almost all of the state maintenance in the framework.

### bots.RandoBot
The random bot implementation

### bots.BetterBot
The heuristic bot implementation

### bots.ModelBot
Uses the starting placement machine learning model

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