import numpy as np
import os

np.set_printoptions(linewidth = 200)

class Minesweeper:
    def __init__(self, dim, nMines):
        #params
        self.dim = dim
        self.nMines = nMines
        #set up mines
        self.mines = np.zeros(dim*dim)
        self.mines[np.random.choice(range(dim*dim), nMines, replace=False)] = 1
	self.mines = self.mines.reshape([dim,dim])
        #set up neighbors
        self.neighbors = np.zeros([dim,dim])
        for i in range(dim):
        	for j in range(dim):
        		nNeighbors = 0
        		for k in range(-1,2):
        			if i+k >= 0 and i+k < dim :
                        		for l in range(-1,2):
        					if j+l >= 0 and j+l < dim and (k != 0 or l != 0):
        		       			    nNeighbors += self.mines[i+k, j+l]
        		self.neighbors[i,j] = nNeighbors
        #set up state
        self.state = np.zeros([dim,dim])
        self.state.fill(np.nan)
    
    def clearEmptyCell(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]
        self.state[x,y] = self.neighbors[x,y]
        if self.state[x,y] == 0:
            for i in range(-1,2):
                if x+i >= 0 and x+i < self.dim:
                    for j in range(-1,2):
                        if y+j >= 0 and y+j < self.dim:
                            if np.isnan(self.state[x+i, y+j]):
                                self.clearEmptyCell((x+i, y+j))
        
    def selectCell(self, coordinates):
        if self.mines[coordinates[0], coordinates[1]] > 0:
            return True     #i.e. gameover is true
        else:
            self.clearEmptyCell(coordinates)
            return False    #i.e. gameover is false
        

def playMinesweeper():

    os.system("clear")
    print "Welcome to Minesweeper, fucker."
    
    dim = input("Enter dimension of game board (one number): ")
    if dim > 10:
        print "Nope. We're doing 10."
        dim = 10
        
    
    nMines = int(0.2*dim*dim)
    game = Minesweeper(dim, nMines)
        
    toss = raw_input("Enter your name: ")
    
    #out of bounds messages
    outOfBoundsMessages = ["Really?", 
        "God you're dumb", 
        "It's really not that hard.", 
        "Wow.",
        "Oh. Okay. Yeah. Yeah that makes sense.    No."]
    
    gameOver = False
    message = "Okay, 'Bitch', let's play."
    while not gameOver:
        if np.sum(np.sum(np.where(np.isnan(game.state), 1, 0))) == game.nMines:
            os.system("clear")
            print game.state
            print "I guess sometimes it's better to be lucky than good. Congratulations."
            return
        else:
            os.system("clear")
            print message
            print "There are " + str(nMines) + " total mines."
            print game.state
            message = "You're still alive, somehow."
            coordinates = input("Enter coordinates: ")
            if isinstance(coordinates, tuple) and coordinates[0] > 0 and coordinates[0] <= dim and coordinates[1] >0 and coordinates[1] <= dim:
                coordinates = (coordinates[0]-1, coordinates[1]-1)
                gameOver = game.selectCell(coordinates)
            else:
                message = outOfBoundsMessages[np.random.randint(0,len(outOfBoundsMessages),1)]
        
    print "Game over idiot."
     

playMinesweeper()   

