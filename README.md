# MineSweeperNeuralNet
Teaching a neural network to play mine sweeper.

Run watchMePlay.py and choose model6. Victory rate is >50% on a 10x10 board with 20 mines (hard).

The goal of this project is to experiment with reinforcement learning, whereby general-purpose neural networks learn to do a task simply by doing it many times and getting some performance feedback. The model doesn’t know the rules of minesweeper, but it figures out how to play anyway. (The model here is a convolutional neural network.)

How good is >50%? Well, an AI with hard-coded Minesweeper logic (including specific end-game strategies) achieved about 50% success on a larger board with the same mine density (https://luckytoilet.wordpress.com/2012/12/23/2125/). So it’s pretty good.

To play the game yourself, run playMineSweeper.py. Be prepared for verbal abuse.