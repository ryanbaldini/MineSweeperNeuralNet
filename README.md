# MineSweeperNeuralNet
Teaching a neural network to play mine sweeper.

Run watchMePlay.py and choose model7. Victory rate is currently around 42% on "Expert": a 16x30 board with 99 mines. See the requirements.txt file if you're having trouble.

To train a new model or continue training a saved one, run trainModel.py.

The goal of this project is to experiment with reinforcement learning, whereby general-purpose neural networks learn to do a task simply by doing it many times and getting some performance feedback. The model doesn’t know the rules of minesweeper, but it figures out how to play anyway. The model here is a convolutional neural network.

How good is ~42%? As a benchmark, another AI with hard-coded Minesweeper logic (including specific end-game strategies) achieved about 50% success on expert (https://luckytoilet.wordpress.com/2012/12/23/2125/). Hopefully the neural net gets there.
