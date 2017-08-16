import numpy as np
import os

np.set_printoptions(linewidth = 500)

#the process:
# model plays n_batch games of minesweeper
# for "choice", assign probability of mine to each cell
# chooses cell with lowest probability
# for the choice, correct probability is either 1 or 0 (i.e. has mine or not)
# so output of keras model is the full array of probabilities
# the selection is then either good...
    # in which case, "correct" array is 0 where the choice was, and equal to the output probabilities elswhere
    # (the latter equating is a trick to make gradients 0 for those cells)
    #and then keep playing
# ... or bad 
    # in which case, "correct" array is 1 where the choice was, and equal to the output probabilities elswhere
    #and you start a new game
#then train on that batch, and go again


#architecture
# have a model library
    #each model specified by script
    #script specifies a keras model
# have model class
    # has model as member 
    # can take any of the models in the model library as its model member function
    # has function learnMinesweeper, which does all the above
        # function specifies number of games per batch, number of batches, etc.
# have script that prompts user to specify model, provide number games, batches,
    # prints out performance as model learns
    # saves model


# the "game board", with state
class MineSweeper:
    def __init__(self, dim, nMines):
        # params
        self.dim = dim
        self.nMines = nMines
        # set up mines
        self.mines = np.zeros(dim * dim)
        self.mines[np.random.choice(range(dim * dim), nMines, replace=False)] = 1
        self.mines = self.mines.reshape([dim, dim])
        # set up neighbors
        self.neighbors = np.zeros([dim, dim])
        for i in range(dim):
            for j in range(dim):
                nNeighbors = 0
                for k in range(-1, 2):
                    if i + k >= 0 and i + k < dim:
                        for l in range(-1, 2):
                            if j + l >= 0 and j + l < dim and (k != 0 or l != 0):
                                nNeighbors += self.mines[i + k, j + l]
                self.neighbors[i, j] = nNeighbors
        # set up state
        self.state = np.zeros([dim, dim])
        self.state.fill(np.nan)
        self.gameOver = False
        self.victory = False

    def clearEmptyCell(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]
        self.state[x, y] = self.neighbors[x, y]
        if self.state[x, y] == 0:
            for i in range(-1, 2):
                if x + i >= 0 and x + i < self.dim:
                    for j in range(-1, 2):
                        if y + j >= 0 and y + j < self.dim:
                            if np.isnan(self.state[x + i, y + j]):
                                self.clearEmptyCell((x + i, y + j))

    def selectCell(self, coordinates):
        if self.mines[coordinates[0], coordinates[1]] > 0:
            self.gameOver = True
            self.victory = False
        else:
            self.clearEmptyCell(coordinates)
            if np.sum(np.isnan(self.state)) == self.nMines:
                self.gameOver = True
                self.victory = True




class MineSweeperLearner:
    def __init__(self, model, dim):
        self.model = model
        self.dim = dim
        self.totalCells = dim*dim
    
    # ultimately want to put this in the model so each can extract its own shit
    def getPredictorsFromGameState(self, state):
        out = np.zeros((1, 10, self.dim, self.dim))
        # out = np.zeros((1, 2, self.dim, self.dim))
        # channel 0: cell is still available
        out[0][0] = np.where(np.isnan(state), 0, 1)
        # the numeric channels: categories from 0 to 8
        for i in range(0,9):
           out[0][i+1] = np.where(state == i, 1, 0)
        #numerics
        # out[0][1] = np.where(np.isnan(state), 0, state)
        return out
    
    def learnMineSweeper(self, gamesPerBatch, nBatches, verbose = True):
        for i in range(nBatches):
            X = np.zeros((1, 10, self.dim, self.dim))    # 10 channels: 1 for each number, 1 for if has been revealed
            X2 = np.zeros((1, 1, self.dim, self.dim))
	    y = np.zeros((1, 1, self.dim, self.dim))
            selectedX = 0
            selectedY = 0
            meanCellsRevealed = 0
            propGamesWon = 0
            for j in range(gamesPerBatch):
                # initiate game
                #print "New game"
                game = MineSweeper(self.dim, int(0.2*self.totalCells))
                while not game.gameOver:
                    # append game state to data input
                    Xnow = self.getPredictorsFromGameState(game.state)
                    # print "here:"
                    #print Xnow
                    X = np.append(X, Xnow, 0)
		    X2now = np.array([[np.where(Xnow[0][0]==0, 1, 0)]]) 
		    #print X2.shape
		    X2 = np.append(X2, X2now,0)
                    out = self.model.predict([Xnow,X2now])
                    #print out
		    # find best remaining option
                    orderedProbs = np.argsort(out[0], axis=None)
		    #print orderedProbs
                    for k in range(self.totalCells):
                        selected = orderedProbs[k]
                        selectedX = int(selected / dim)
                        selectedY = selected % dim
                        if np.isnan(game.state[selectedX, selectedY]):
                            break
                    game.selectCell((selectedX, selectedY))
                    #find truth
                    truth = out
                    truth[0,0,selectedX, selectedY] = game.mines[selectedX, selectedY] # can do this; clicking reveals state
                    #truth = np.array([[game.mines]]) #cheating
		    y = np.append(y, truth, 0)
                    #print truth
                meanCellsRevealed += self.totalCells - np.sum(np.isnan(game.state))
                if game.victory:
                    propGamesWon += 1
            meanCellsRevealed = float(meanCellsRevealed) / gamesPerBatch
            propGamesWon = float(propGamesWon) / gamesPerBatch
            if verbose:
                print "Mean cells revealed, batch " + str(i) + ": " + str(meanCellsRevealed)
                print "Proportion of games won, batch " + str(i) + ": " + str(propGamesWon)
            #now do training
            X = np.delete(X,0,0)
	    X2 = np.delete(X2,0,0)
            y = np.delete(y,0,0)
            #print y
            self.model.fit([X,X2],y,epochs=1)


dim = 10

from keras.optimizers import SGD, RMSprop, Adadelta
from keras.models import Sequential, Model, load_model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import Multiply
#from keras.layers.local import LocallyConnected2D
inputShape = (10,dim,dim)

#model = Sequential()
#model.add(Conv2D(8, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True, input_shape=inputShape))
#model.add(Conv2D(8, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True))
#model.add(Conv2D(1, (1,1), padding='same', data_format = 'channels_first', activation = 'sigmoid', use_bias = True))
#model.compile(loss='binary_crossentropy',optimizer=SGD(lr=0.01*dim*dim, momentum = 0.5, nesterov=True))
#model.summary()

in1 = Input(shape=inputShape)
in2 = Input(shape=(1,dim,dim))
conv = Conv2D(16, (5,5), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(in1)
conv = Conv2D(8, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(1, (1,1), padding='same', data_format = 'channels_first', activation = 'sigmoid', use_bias = True)(conv)
out = Multiply()([conv,in2])
model = Model(inputs=[in1,in2], outputs=out)
model.compile(loss='binary_crossentropy',optimizer='adadelta')

#now do it
learner = MineSweeperLearner(model, dim)
learner.learnMineSweeper(gamesPerBatch=100, nBatches=100000, verbose=True)

#save model
learner.model.save('models/model1.h5')
