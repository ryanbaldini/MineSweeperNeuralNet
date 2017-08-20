import numpy as np
import os
from MineSweeper import MineSweeper

np.set_printoptions(linewidth = 200)

def playMinesweeper():

    os.system("clear")
    print "Welcome to Minesweeper, fucker."
    
    dim = input("Enter dimension of game board (one number): ")
    if dim > 10:
        print "Don't waste my time. We're doing 10."
        dim = 10
    
    nMines = int(0.2*dim*dim)
        
    toss = raw_input("Enter your name: ")
    
    #out of bounds messages
    outOfBoundsMessages = ["Really?", 
        "God you're dumb", 
        "It's really not that hard.", 
        "Wow.",
        "Oh. Okay. Yeah. Yeah that makes sense.    No."]

    playing = True
    while playing:
        message = "Okay, 'Bitch', let's play."
        game = MineSweeper(dim, nMines)
        while not game.gameOver:
            os.system("clear")
            print message
            print "There are " + str(nMines) + " total mines."
            print game.state
            message = "You're still alive, somehow."
            coordinates = input("Enter coordinates: ")
            if isinstance(coordinates, tuple) and coordinates[0] > 0 and coordinates[0] <= dim and coordinates[1] >0 and coordinates[1] <= dim:
                coordinates = (coordinates[0]-1, coordinates[1]-1)
                game.selectCell(coordinates)
            else:
                message = outOfBoundsMessages[np.random.randint(0,len(outOfBoundsMessages),1)[0]]
        if game.victory:
            os.system("clear")
            print game.state
            print "I guess sometimes it's better to be lucky than good. Congratulations."
        else:
            print "Game over idiot."

        again = raw_input("Play again? (y/n)")
        if again != "y":
            playing = False
            print "Yeah, this is probably not your game anyway."

playMinesweeper()   

