import numpy as np
from MineSweeper import MineSweeper
import time
import os

class MineSweeperLearner:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.dim1 = 16
        self.dim2 = 30
        self.totalCells = self.dim1*self.dim2

    # ultimately want to put this in the model so each can extract its own shit
    def getPredictorsFromGameState(self, state):
        out = np.zeros((11, self.dim1, self.dim2))
        # channel 0: cell is still available to be clicked on
        out[0] = np.where(np.isnan(state), 0, 1)
        # channel 1: cell is on game board (useful for detecting edges when conv does 0 padding)
        out[1] = np.ones((self.dim1, self.dim2))
        # the numeric channels: one layer each for 0 to 8 neighbors; one-hot encoding
        for i in range(0, 9):
            out[i + 2] = np.where(state == i, 1, 0)
        return out

    def learnMineSweeper(self, nSamples, nBatches, nEpochsPerBatch, verbose=True):
        X = np.zeros((nSamples, 11, self.dim1, self.dim2))  # 11 channels: 1 for if has been revealed, 1 for is-on-board, 1 for each number
        X2 = np.zeros((nSamples, 1, self.dim1, self.dim2))
        y = np.zeros((nSamples, 1, self.dim1, self.dim2))
        for i in range(nBatches):
            cellsRevealed = 0
            gamesPlayed = 0
            gamesWon = 0
            samplesTaken = 0
            while samplesTaken < nSamples:
                # initiate game
                game = MineSweeper()
                #pick middle on first selection. better than corner.
                game.selectCell((self.dim1/2, self.dim2/2))
                while not (game.gameOver or samplesTaken == nSamples):
                    # get data input from game state
                    Xnow = self.getPredictorsFromGameState(game.state)
                    X[samplesTaken] = Xnow
                    X2now = np.array([np.where(Xnow[0] == 0, 1, 0)])
                    X2[samplesTaken] = X2now
                    # make probability predictions
                    out = self.model.predict([np.array([Xnow]), np.array([X2now])])
                    # choose best remaining cell
                    orderedProbs = np.argsort(out[0][0]+Xnow[0], axis=None) #add Xnow[0] so that already selected cells aren't chosen
                    selected = orderedProbs[0]
                    selected1 = int(selected / self.dim2)
                    selected2 = selected % self.dim2
                    game.selectCell((selected1, selected2))
                    # find truth
                    truth = out
                    truth[0, 0, selected1, selected2] = game.mines[selected1, selected2]
                    y[samplesTaken] = truth[0]
                    samplesTaken += 1
                if game.gameOver:
                    gamesPlayed += 1
                    cellsRevealed += self.totalCells - np.sum(np.isnan(game.state))
                    if game.victory:
                        gamesWon += 1
            meanCellsRevealed = float(cellsRevealed) / gamesPlayed
            propGamesWon = float(gamesWon) / gamesPlayed
            if verbose:
                print "Games played, batch " + str(i) + ": " + str(gamesPlayed)
                print "Mean cells revealed, batch " + str(i) + ": " + str(meanCellsRevealed)
                print "Proportion of games won, batch " + str(i) + ": " + str(propGamesWon)
            #train
            self.model.fit([X, X2], y, epochs=nEpochsPerBatch)
            #save it every 100
            if (i+1) % 100 == 0:
                self.model.save("trainedModels/" + self.name + ".h5")

    def watchMePlay(self):
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
            time.sleep(0.1)
            os.system("clear")
            #now the rest
            while not game.gameOver:
                print "Last selection: (" + str(selected1+1) + "," + str(selected2+1) + ")"
                print "Game board:"
                print game.state
                Xnow = self.getPredictorsFromGameState(game.state)
                X2now = np.array([np.where(Xnow[0] == 0, 1, 0)])
                # make probability predictions
                out = self.model.predict([np.array([Xnow]), np.array([X2now])])
                # choose best remaining cell
                orderedProbs = np.argsort(out[0][0] + Xnow[0], axis=None)  # add Xnow[0] so that already selected cells aren't chosen
                selected = orderedProbs[0]
                selected1 = int(selected / self.dim2)
                selected2 = selected % self.dim2
                game.selectCell((selected1, selected2))
                time.sleep(0.1)
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
