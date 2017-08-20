import numpy as np
from MineSweeper import MineSweeper
import time
import os

class MineSweeperLearner:
    def __init__(self, name, model, dim):
        self.name = name
        self.model = model
        self.dim = dim
        self.totalCells = dim * dim

    # ultimately want to put this in the model so each can extract its own shit
    def getPredictorsFromGameState(self, state):
        out = np.zeros((1, 11, self.dim, self.dim))
        # channel 0: cell is still available to be clicked on
        out[0][0] = np.where(np.isnan(state), 0, 1)
        # channel 1: cell is on game board (useful for detecting edges when conv does 0 padding)
        out[0][1] = np.ones((self.dim, self.dim))
        # the numeric channels: one layer each for 0 to 8 neighbors; one-hot encoding
        for i in range(0, 9):
            out[0][i + 2] = np.where(state == i, 1, 0)
        return out

    def learnMineSweeper(self, gamesPerBatch, nBatches, nEpochsPerBatch, verbose=True):
        for i in range(nBatches):
            X = np.zeros((1, 11, self.dim, self.dim))  # 11 channels: 1 for if has been revealed, 1 for is-on-board, 1 for each number
            X2 = np.zeros((1, 1, self.dim, self.dim))
            y = np.zeros((1, 1, self.dim, self.dim))
            meanCellsRevealed = 0
            propGamesWon = 0
            for j in range(gamesPerBatch):
                # initiate game
                game = MineSweeper(self.dim, int(0.2 * self.totalCells))
                #pick middle on first selection. better than corner.
                game.selectCell((self.dim/2, self.dim/2))
                while not game.gameOver:
                    # get data input from game state
                    Xnow = self.getPredictorsFromGameState(game.state)
                    X = np.append(X, Xnow, 0)
                    X2now = np.array([[np.where(Xnow[0][0] == 0, 1, 0)]])
                    X2 = np.append(X2, X2now, 0)
                    # make probability predictions
                    out = self.model.predict([Xnow, X2now])
                    # choose best remaining cell
                    orderedProbs = np.argsort(out[0][0]+Xnow[0][0], axis=None) #add Xnow[0] so that already selected cells aren't chosen
                    selected = orderedProbs[0]
                    selectedX = int(selected / self.dim)
                    selectedY = selected % self.dim
                    game.selectCell((selectedX, selectedY))
                    # find truth
                    truth = out
                    truth[0, 0, selectedX, selectedY] = game.mines[selectedX, selectedY]
                    y = np.append(y, truth, 0)
                meanCellsRevealed += self.totalCells - np.sum(np.isnan(game.state))
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
        np.set_printoptions(linewidth=200)
        play = True
        while play:
            game = MineSweeper(self.dim, int(0.2 * self.totalCells))
            os.system("clear")
            print "Beginning play"
            print "Game board:"
            print game.state
            #make first selection in the middle. better than corner.
            selectedX = self.dim/2
            selectedY = self.dim/2
            game.selectCell((selectedX, selectedY))
            time.sleep(0.25)
            os.system("clear")
            #now the rest
            while not game.gameOver:
                print "Last selection: (" + str(selectedX+1) + "," + str(selectedY+1) + ")"
                print "Game board:"
                print game.state
                Xnow = self.getPredictorsFromGameState(game.state)
                X2now = np.array([[np.where(Xnow[0][0] == 0, 1, 0)]])
                # make probability predictions
                out = self.model.predict([Xnow, X2now])
                # choose best remaining cell
                orderedProbs = np.argsort(out[0][0] + Xnow[0][0], axis=None)  # add Xnow[0] so that already selected cells aren't chosen
                selected = orderedProbs[0]
                selectedX = int(selected / self.dim)
                selectedY = selected % self.dim
                game.selectCell((selectedX, selectedY))
                time.sleep(0.25)
                os.system("clear")
            if np.sum(np.isnan(game.state)) < self.totalCells:
                print "Last selection: (" + str(selectedX+1) + "," + str(selectedY+1) + ")"
            print "Game board:"
            print game.state
            if game.victory:
                print "Victory!"
            else:
                print "Game Over"
            get = raw_input("Watch me play again? (y/n): ")
            if get != "y":
                play = False
