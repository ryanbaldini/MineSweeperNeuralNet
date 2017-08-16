import numpy as np

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
