import numpy as np

# the "game board", with state
class MineSweeper:
    def __init__(self, dim, nMines):
        # params
        self.dim = dim
        self.totalCells = dim*dim
        self.nMines = nMines
        self.mines = np.zeros([dim, dim])
        self.neighbors = np.zeros([dim, dim])
        self.state = np.zeros([dim, dim])
        self.state.fill(np.nan)
        self.initialized = False
        self.gameOver = False
        self.victory = False

    def initialize(self, coordinates):    #not run until after first selection!
        # set up mines
        # randomly place mines anywhere *except* first selected location AND surrounding cells
        # so that first selection is always a 0
        # weird, yes, but that's how the original minesweeper worked
        availableCells = range(self.totalCells)
        selected = coordinates[0]*self.dim + coordinates[1]
        offLimits = np.array([selected-self.dim-1, selected-self.dim, selected-self.dim+1, selected-1, selected, selected+1, selected+self.dim-1, selected+self.dim, selected+self.dim+1])    #out of bounds is ok
        availableCells = np.setdiff1d(availableCells, offLimits)
        self.nMines = np.minimum(self.nMines, len(availableCells))  #in case there are fewer remaining cells than mines to place
        minesFlattened = np.zeros([self.dim*self.dim])
        minesFlattened[np.random.choice(availableCells, self.nMines, replace=False)] = 1
        self.mines = minesFlattened.reshape([self.dim, self.dim])
        # set up neighbors
        for i in range(self.dim):
            for j in range(self.dim):
                nNeighbors = 0
                for k in range(-1, 2):
                    if i + k >= 0 and i + k < self.dim:
                        for l in range(-1, 2):
                            if j + l >= 0 and j + l < self.dim and (k != 0 or l != 0):
                                nNeighbors += self.mines[i + k, j + l]
                self.neighbors[i, j] = nNeighbors
        #done
        self.initialized = True

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
        if self.mines[coordinates[0], coordinates[1]] > 0:  #condition always fails on first selection
            self.gameOver = True
            self.victory = False
        else:
            if not self.initialized:    #runs after first selection
                self.initialize(coordinates)
            self.clearEmptyCell(coordinates)
            if np.sum(np.isnan(self.state)) == self.nMines:
                self.gameOver = True
                self.victory = True
