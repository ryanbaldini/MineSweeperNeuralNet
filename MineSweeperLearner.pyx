import numpy as np
cimport numpy as np
#from MineSweeper import MineSweeper
import time
import os

# the "game board", with state
cdef class MineSweeper:
    cdef int dim1
    cdef int dim2
    cdef int totalCells
    cdef int nMines
    cdef int initialized
    cdef int gameOver
    cdef int victory
    cdef np.ndarray mines
    cdef np.ndarray neighbors
    cdef np.ndarray state

    def __init__(self):
        self.dim1 = 16
        self.dim2 = 30
        self.totalCells = self.dim1 * self.dim2
        self.nMines = 99
        self.mines = np.zeros([self.dim1, self.dim2])
        self.neighbors = np.zeros([self.dim1, self.dim2])
        self.state = np.zeros([self.dim1, self.dim2])
        self.state.fill(np.nan)
        self.initialized = 0
        self.gameOver = 0
        self.victory = 0

    def initialize(self, coordinates):    #not run until after first selection!
        # set up mines
        # randomly place mines anywhere *except* first selected location AND surrounding cells
        # so that first selection is always a 0
        # weird, yes, but that's how the original minesweeper worked
        availableCells = range(self.totalCells)
        selected = coordinates[0]*self.dim2 + coordinates[1]
        offLimits = np.array([selected-self.dim2-1, selected-self.dim2, selected-self.dim2+1, selected-1, selected, selected+1, selected+self.dim2-1, selected+self.dim2, selected+self.dim2+1])    #out of bounds is ok
        availableCells = np.setdiff1d(availableCells, offLimits)
        self.nMines = np.minimum(self.nMines, len(availableCells))  #in case there are fewer remaining cells than mines to place
        minesFlattened = np.zeros([self.totalCells])
        minesFlattened[np.random.choice(availableCells, self.nMines, replace=False)] = 1
        self.mines = minesFlattened.reshape([self.dim1, self.dim2])
        # set up neighbors
        cdef int i
        cdef int j
        cdef int k
        cdef int l
        cdef int nNeighbors
        for i in range(self.dim1):
            for j in range(self.dim2):
                nNeighbors = 0
                for k in range(-1, 2):
                    if i + k >= 0 and i + k < self.dim1:
                        for l in range(-1, 2):
                            if j + l >= 0 and j + l < self.dim2 and (k != 0 or l != 0):
                                nNeighbors += self.mines[i + k, j + l]
                self.neighbors[i, j] = nNeighbors
        #done
        self.initialized = 1

    def clearEmptyCell(self, coordinates):
        cdef int x
        cdef int y
        x = coordinates[0]
        y = coordinates[1]
        self.state[x, y] = self.neighbors[x, y]
        cdef int i
        cdef int j
        if self.state[x, y] == 0:
            for i in range(-1, 2):
                if x + i >= 0 and x + i < self.dim1:
                    for j in range(-1, 2):
                        if y + j >= 0 and y + j < self.dim2:
                            if np.isnan(self.state[x + i, y + j]):
                                self.clearEmptyCell((x + i, y + j))

    def selectCell(self, coordinates):
        if self.mines[coordinates[0], coordinates[1]] > 0:  #condition always fails on first selection
            self.gameOver = 1
            self.victory = 0
        else:
            if not self.initialized:    #runs after first selection
                self.initialize(coordinates)
            self.clearEmptyCell(coordinates)
            if np.sum(np.isnan(self.state)) == self.nMines:
                self.gameOver = 1
                self.victory = 1

class MineSweeperLearner:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.dim1 = 16
        self.dim2 = 30
        self.totalCells = self.dim1*self.dim2

    # ultimately want to put this in the model so each can extract its own shit
    def getPredictorsFromGameState(self, np.ndarray state):
        out = np.zeros((1, 11, self.dim1, self.dim2))
        # channel 0: cell is still available to be clicked on
        out[0][0] = np.where(np.isnan(state), 0, 1)
        # channel 1: cell is on game board (useful for detecting edges when conv does 0 padding)
        out[0][1] = np.ones((self.dim1, self.dim2))
        # the numeric channels: one layer each for 0 to 8 neighbors; one-hot encoding
        cdef int i
        for i in range(0, 9):
            out[0][i + 2] = np.where(state == i, 1, 0)
        return out

    def learnMineSweeper(self, int gamesPerBatch, int nBatches, int nEpochsPerBatch, verbose=True):
        cdef int i
        cdef int j
        for i in range(nBatches):
            X = np.zeros((1, 11, self.dim1, self.dim2))  # 11 channels: 1 for if has been revealed, 1 for is-on-board, 1 for each number
            X2 = np.zeros((1, 1, self.dim1, self.dim2))
            y = np.zeros((1, 1, self.dim1, self.dim2))
            meanCellsRevealed = 0
            propGamesWon = 0
            for j in range(gamesPerBatch):
                t0 = time.time()
                t = 0.0
                tAppend = 0.0
                # initiate game
                game = MineSweeper()
                #pick middle on first selection. better than corner.
                game.selectCell((self.dim1/2, self.dim2/2))
                while not game.gameOver:
                    # get data input from game state
                    Xnow = self.getPredictorsFromGameState(game.state)
                    ta = time.time()
                    X = np.append(X, Xnow, 0)
                    X2now = np.array([[np.where(Xnow[0][0] == 0, 1, 0)]])
                    X2 = np.append(X2, X2now, 0)
                    tb = time.time()
                    print tb-ta
                    tAppend += tb-ta
                    # make probability predictions
                    t1 = time.time()
                    out = self.model.predict([Xnow, X2now])
                    t2 = time.time()
                    t += t2 - t1
                    # choose best remaining cell
                    orderedProbs = np.argsort(out[0][0]+Xnow[0][0], axis=None) #add Xnow[0] so that already selected cells aren't chosen
                    selected = orderedProbs[0]
                    selected1 = int(selected / self.dim2)
                    selected2 = selected % self.dim2
                    game.selectCell((selected1, selected2))
                    # find truth
                    truth = out
                    truth[0, 0, selected1, selected2] = game.mines[selected1, selected2]
                    ta = time.time()
                    y = np.append(y, truth, 0)
                    tb = time.time()
                    tAppend += tb-ta
                    print tb-ta
                meanCellsRevealed += self.totalCells - np.sum(np.isnan(game.state))
                t3 = time.time()
                print "Proportion time in prediction: " + str(t/(t3-t0))
                print "Proportion time in appending: " + str(tAppend/(t3-t0))
                if game.victory:
                    propGamesWon += 1
            meanCellsRevealed = float(meanCellsRevealed) / gamesPerBatch
            propGamesWon = float(propGamesWon) / gamesPerBatch
            if verbose:
                print "Mean cells revealed, batch " + str(i) + ": " + str(meanCellsRevealed)
                print "Proportion of games won, batch " + str(i) + ": " + str(propGamesWon)
            # now train on data
            X = np.delete(X, 0, 0)
            X2 = np.delete(X2, 0, 0)
            y = np.delete(y, 0, 0)
            # print y
            self.model.fit([X, X2], y, epochs=nEpochsPerBatch)
            #save it every 100
            if (i+1) % 100 == 0:
                self.model.save("trainedModels/" + self.name + ".h5")

    def watchMePlay(self):
        cdef int play
        np.set_printoptions(linewidth=200)
        play = True
        while play:
            game = MineSweeper()
            os.system("clear")
            print "Beginning play"
            print "Game board:"
            print game.state
            #make first selection in the middle. better than corner.
            selected1 = self.dim1/2
            selected2 = self.dim2/2
            game.selectCell((selected1, selected2))
            time.sleep(0.25)
            os.system("clear")
            #now the rest
            while not game.gameOver:
                print "Last selection: (" + str(selected1+1) + "," + str(selected2+1) + ")"
                print "Game board:"
                print game.state
                Xnow = self.getPredictorsFromGameState(game.state)
                X2now = np.array([[np.where(Xnow[0][0] == 0, 1, 0)]])
                # make probability predictions
                out = self.model.predict([Xnow, X2now])
                # choose best remaining cell
                orderedProbs = np.argsort(out[0][0] + Xnow[0][0], axis=None)  # add Xnow[0] so that already selected cells aren't chosen
                selected = orderedProbs[0]
                selected1 = int(selected / self.dim2)
                selected2 = selected % self.dim2
                game.selectCell((selected1, selected2))
                time.sleep(0.25)
                os.system("clear")
            if np.sum(np.isnan(game.state)) < self.totalCells:
                print "Last selection: (" + str(selected1+1) + "," + str(selected2+1) + ")"
            print "Game board:"
            print game.state
            if game.victory:
                print "Victory!"
            else:
                print "Game Over"
            get = raw_input("Watch me play again? (y/n): ")
            if get != "y":
                play = False
