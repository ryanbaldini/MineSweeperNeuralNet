import numpy as np
cimport numpy as np

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
