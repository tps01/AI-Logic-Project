#Authors: Tom Sullivan & Jack Hoy (Prof. Fitzsimmons for gridVariables loop from HW#3)
#Last Updated: 11/04/2022
#Project 2 Artificial Intelligence

import sys
from pysat.solvers import Glucose3
from itertools import combinations

def read_board(filename):
    board_file = open(filename) #open file into map_file
    map = board_file.readlines() #create list where each element is a row on map
    for i in range(0, len(map)):
        map[i] = map[i].strip() #iterate through map and remove \n characters
    return(map) #return map

def isTop(board,r,c):#returns true if the current square is in the top row (otherwise false).
    top=False
    if(r == 0):
        top = True
    return top
def isBot(board,r,c):#returns true if the current square is in the bottom row (otherwise false).
    bot=False
    if(r == len(board)-1):
        bot = True
    return bot
def isRight(board,r,c):#returns true if the current square is in the right-most column (otherwise false).
    right=False
    if(c == len(board[0])-1):
        right = True
    return right
def isLeft(board,r,c):#returns true if the current square is in the left-most column (otherwise false).
    left=False
    if(c == 0):
        left = True
    return left


#adj_count returns the amount of unavailable adjacent squares, with sides of the board counting as unavailable squares
#This is used both to detect if a puzzle cannot be solved and to determine which clauses to add for certain number squares*.
#*For example, a '2' tile with an 'X' next to it uses different CNF clauses than a '2' tile with no adjacent blocking tiles or walls.
def adj_count(twoDarray,r,c): 
    count=0
    blockers = 'X01234'
    if(isTop(twoDarray,r,c)): #top of board
        count+=1
    if(isLeft(twoDarray,r,c)): #left wall
        count+=1
    if(isBot(twoDarray,r,c)): #bottom of board
        count+=1
    if(isRight(twoDarray,r,c)): #right wall   
        count+=1
    if(not(isTop(twoDarray,r,c))): #If the square above the current tile is X, 0, 1, 2, 3, or 4
        if(twoDarray[r-1][c] in blockers):
            count+=1
    if(not(isBot(twoDarray,r,c))): #If the square below the current tile is X, 0, 1, 2, 3, or 4
        if(twoDarray[r+1][c] in blockers):
            count+=1
    if(not(isRight(twoDarray,r,c))): #If the square to the right of the current tile is X, 0, 1, 2, 3, or 4
        if(twoDarray[r][c+1] in blockers):
            count+=1
    if(not(isLeft(twoDarray,r,c))): #If the square to the left of the current tile is X, 0, 1, 2, 3, or 4
        if(twoDarray[r][c-1] in blockers):
            count+=1
    return count 
#end adj_count


#Available() returns a list of the available squares next to the tile being checked. 
#i.e. squares that are not walls, Xs, 0s, 1s, 2s, 3s, or 4s.
#an example: In the below function, where the tile being checked is the '1',
#the list [2,4] would be returned. All tiles follow the same gridVariables naming convention as in main().
#...
#.1X
def Available(board,r,c):
    blockers = 'X01234' # A string containing all invalid tiles for placing a light. (can be iterated through in python)
    val = 1 # The loop below creates a 2D array that coincides with the board, with a value for each position. (Taken from the rooks.py starter code for HW#3, and left unchanged.)
    output = {}
    gridVariables = dict()
    for r1 in range(len(board)):
        for c1 in range(len(board[r1])):
            gridVariables[(r1,c1)] = val
            output[val] = (r1,c1)
            val += 1 #end board values
    available_squares = [] #Create an empty list to fill with available squares.
    if(not(isTop(board,r,c))):#Checks that the current tile is not at the top of the board to avoid bad indexing, then checks the tile above to see if a light can be placed there.
        if(board[r-1][c] not in blockers):
            available_squares.append(gridVariables[(r-1,c)])
    if(not(isBot(board,r,c))):#Same as the top check, but for the tile below.
        if(board[r+1][c] not in blockers):
            available_squares.append(gridVariables[(r+1,c)])
    if(not(isLeft(board,r,c))):#Same as previous checks, but for tile to the left.
        if(board[r][c-1] not in blockers):
            available_squares.append(gridVariables[(r,c-1)])
    if(not(isRight(board,r,c))):#Same as previous checks, but for tile to the right.
        if(board[r][c+1] not in blockers):
            available_squares.append(gridVariables[(r,c+1)])
    return available_squares#return the list of available tiles, named in the gridVariables convention established in main().



#Returns the result of the itertools "combinations" function. 
#An example: Combos([1,2,3],2) returns [(1,2),(1,3),(2,3)]
#These are all of the possible combinations of length two, given the set of 3 numbers.
#This would not produce a result like [(1,2),(2,1),....], where a combination is flipped.
def Combos(list1, r):
    return list(combinations(list1, r))


#The lightup program:
#Given a maze as a command line argument, lightup.py will attempt to solve the puzzle given the rules of the lightup game.
#More information on the rules of the game can be found in project2.pdf.
def main():
    boardFile = sys.argv[1]#Get file from command line argument
    board = read_board(boardFile) #name the file "board."
    print("Original board:")#For readability in the command line output.
    for i in range(len(board)):#This loop prints out the original board passed in the command line. (In reality, this will print any text file you pass as an argument line-by-line.)
        print(board[i])
    print('\n')
    blockers = 'X01234' # A string containing the tiles that lights cannot be placed on and stop light.

    val = 1 # The loop below creates a 2D array that coincides with the board, with a value for each position. (Taken from the rooks.py starter code for HW#3, and left unchanged.)
    output = {}
    gridVariables = dict()
    for r in range(len(board)):
        for c in range(len(board[r])):
            gridVariables[(r,c)] = val
            output[val] = (r,c)
            val += 1 #end board values

    phi = Glucose3()#This is the SAT solver that will solve our problem, once we add CNF clauses to it.



#___________________________________________________________________________"rooks" case
#In the lightup puzzle, two lights cannot have direct line of sight to one another.
#This loop addresses that constraint. We call this the "rooks" case because it is similar to the N-Rooks problem.

    for r in range(len(board)):#Iterate through rows and columns, checking each square individually.
        for c in range(len(board[0])):
            if(board[r][c] in blockers):#If the current tile being checked is a 0, 1, 2, 3, 4, or X, skip it-- lights cannot pass through or be placed on this square.
                continue
            if(not(isRight(board,r,c))):# As long as we aren't checking the right-most row, make sure that the current square and all squares to the right (stopping at blocking tiles) do not have a light on them at the same time.
                for i in range(c+1,len(board[0])):# Iterate to the right
                    if(board[r][i] in blockers): # If the tile being checked against the current tile is a blocking tile, stop checking it and the squares to the right of it. (It blocks line of sight)
                        break
                    else:#Otherwise, the two squares do have line of sight, and we add a clause to make sure both squares do not have a light at the same time.
                        row_clause = [-1*abs(gridVariables[(r,c)]),-1*abs(gridVariables[(r,i)])]
                        phi.add_clause(row_clause)
            if(not(isBot(board,r,c))):# This is the same idea as checking to the right, but we move down the board instead of to the right. Once again, we stop when we see a blocking tile.
                for i in range(r+1, len(board)):
                    if(board[i][c] in blockers):
                        break
                    else:
                        col_clause = [-1*abs(gridVariables[(r,c)]),-1*abs(gridVariables[(i,c)])]
                        phi.add_clause(col_clause)

#We do not check to left left and up from our current tile, because that would only create duplicate clauses after checking every square.                         
#___________________________________________________________________________end "rooks" case



#___________________________________________________________________________all squares lit case
#In the lightup puzzle, every square needs to be lit up by having line of sight with a light bulb.
#In this section we loop through every square and we add a clause that specifies this rule.
#This can be boiled down to checking a "plus-sign" at each square-- making sure that out of the set of all the tiles, in every direction,
#that the current tile has line of sight to, there is at least one lightbulb. (This does not mean *exactly* one bulb-- a tile can be lit by multiple lightbulbs.)

    for r in range(len(board)):#Loop through board, checking each tile.
        for c in range(len(board[0])): 
            if(board[r][c] in blockers):# Blocking tiles block light, so we do not check them.
                continue
            lit_list = []#Create a list of all the tiles that the current square can see. (Initially empty for clarity.)
            lit_list.append(abs(gridVariables[(r,c)]))#Add the current tile into the list, as a lightbulb can light up its own square.
            if(not(isRight(board,r,c))):#If not at right of the board, begin adding tiles to the right.
                for i in range(c+1,len(board[0])):
                    if(board[r][i] in blockers):#If the tile being looked at is a blocking tile, stop looking in this direction. The line of sight stops here, and further tiles need not be considered.
                        break
                    else:#If the tile being compared has line of sight, add it to the list.
                        lit_list.append(abs(gridVariables[(r,i)]))
            if(not(isLeft(board,r,c))):#The same as the above condition, but to the left. 
                for i in range(c-1,-1,-1):#The difference in this range involves the negative numbers-- This says start at the column to the left of the current column, and iterate by -1, until you reach 0. This range excludes -1; it stops at 0, which is the leftmost column.
                    if(board[r][i] in blockers):
                        break
                    else:
                        lit_list.append(abs(gridVariables[(r,i)]))
            if(not(isBot(board,r,c))):#Similar to above conditions, but this iterates downward.
                for i in range(r+1, len(board)):
                    if(board[i][c] in blockers):
                        break
                    else:
                        lit_list.append(abs(gridVariables[(i,c)]))
            if(not(isTop(board,r,c))):#Similar to above conditions, but this iterates upward.
                for i in range(r-1,-1,-1):#This is similar to the iterate-left condition, where the range is incrementing by -1 each time, stopping at row 0 (the top row).
                    if(board[i][c] in blockers):
                        break
                    else:
                        lit_list.append(abs(gridVariables[(i,c)]))
            phi.add_clause(lit_list)#Add all of the visible spaces in a list as a clause. This is one large "OR" clause, which states that there needs to be at least one light in all of those tiles.
#___________________________________________________________________________end all lit case
    
#----- number handling
    for r in range(len(board)):#Iterate through all squares
        for c in range(len(board[0])):
            #If the current square is a 0
            if (board[r][c]== '0'):
                open_squares0 = Available(board,r,c)#Find all open squares next to the '0' square.
                for i in range(len(open_squares0)): 
                    phi.add_clause([-1*abs(open_squares0[i])])#Iterate through these squares, and set all to false. (No lights placed in those squares)

            #If current square is a 1
            if (board[r][c]== '1'):
                if(adj_count(board,r,c) == 4):#If the '1' is surrounded by obstacles or walls on all sides, the puzzle is unsolvable.
                    phi.add_clause([1]) #add a 1 and -1 clause seperately, so that the SAT solver can only return false.
                    phi.add_clause([-1])
                else:
                    open_squares = Available(board,r,c)#Find available squares next to the 1.
                    phi.add_clause(open_squares)#At least one of these squares needs a light in it.
                    for i in range(len(open_squares)):#This nested loop specifies that no two available squares can have a light in them at the same time. (At most one true)
                        for j in range(i+1,len(open_squares)):
                            phi.add_clause([-1*abs(open_squares[i]),-1*abs(open_squares[j])]) #A => not B, for each combination of squares.
                            #print([-1*abs(open_squares[i]),-1*abs(open_squares[j])])

            #If current square is a 2
            if (board[r][c]== '2'):
                if(adj_count(board,r,c) >= 3):#If there are 3 obstacles/walls surrounding the 2, the puzzle is unsolvable.
                    phi.add_clause([1])
                    phi.add_clause([-1])

                elif(adj_count(board,r,c) == 0):# no obstacles surrounding number 2-- four open tiles.
                    open_squares2 = Available(board,r,c)
                    orlist = Combos(open_squares2,3) #Create all combinations of three of the 4 squares. In total, this means that two of the four squares need lights (be true/positive numbers).
                    for i in range(len(open_squares2)):#negate all open square values, to create next clause.
                        open_squares2[i] = -1*abs(open_squares2[i])
                    ornotlist = Combos(open_squares2,3)#Create a list of all combinations of three negated available squares. This specifies that at least 2 of the four squares need to be false.
                    for j in range(len(orlist)):#Add all of the clauses to phi, specifying that at least two squares need to be true, and at least two false. This means exactly 2 sqaures have lights.
                        phi.add_clause(orlist[j])
                        phi.add_clause(ornotlist[j])

                elif(adj_count(board,r,c) == 1):# 1 obstacle next to number 2
                    open_squares2 = Available(board,r,c)
                    orlist = Combos(open_squares2,2)#Create combinations of the available squares. With all combinations, this states that at least two of the available squares need lights.
                    for i in range(len(open_squares2)):
                        open_squares2[i] = -1*abs(open_squares2[i])#negate the values of the available squares, creating a clause like [-A,-B,-C]. This means at least one square must be false.
                    phi.add_clause(open_squares2)#one square must be false.
                    for j in range(len(orlist)):#Add all of the combinations of squares (non-negated).
                        phi.add_clause(orlist[j])#Two squares must be true.

                else:# two obstacles next to number 2
                    open_squares2 = Available(board,r,c)
                    for i in range(len(open_squares2)):#Since there are only two open squares, state that those two squares must have lights in them.
                        phi.add_clause([open_squares2[i]])

            #If current square is a 3
            if (board[r][c]== '3'):
                if(adj_count(board,r,c) >= 2):#If there are 2 obstacles/walls surrounding the 3, the puzzle is unsolvable.
                    phi.add_clause([1])
                    phi.add_clause([-1])

                elif(adj_count(board,r,c) == 1):#one obstacle, 3 open squares
                    open_squares3 = Available(board,r,c)
                    for i in range(len(open_squares3)):#Since there is an obstacle, we already know which three squares need lights. We set those squares to be true.
                        phi.add_clause([abs(open_squares3[i])])

                else: # four open squares, need 3 lights
                    open_squares3 = Available(board,r,c)
                    orlist3 = Combos(open_squares3,2)#Find all 2-length combinations of the squares.
                    for i in range(len(orlist3)):#All of these clauses together state that at least 3 squares must be true.
                        phi.add_clause(orlist3[i])
                    for j in range(len(open_squares3)):#negate all squares for the next clause
                        open_squares3[j] = -1*open_squares3[j]
                    phi.add_clause(open_squares3)#This clause is all of the available squares negated and "ORed" together. It states that at least 1 square needs to be false.

            if (board[r][c]== '4'):
                if(adj_count(board,r,c) >= 1):#If there is an obstacle/wall next to the 4, the puzzle is unsolvable.
                    phi.add_clause([1])
                    phi.add_clause([-1])
                else: #If the program makes it here, all of the squares around the 4 are available. Specify that all of them are true.
                    phi.add_clause([1*abs(gridVariables[(r-1,c)])])#above
                    phi.add_clause([1*abs(gridVariables[(r+1,c)])])#below
                    phi.add_clause([1*abs(gridVariables[(r,c+1)])])#right
                    phi.add_clause([1*abs(gridVariables[(r,c-1)])])#left
        
#----- end number handling

#-----obstacles are false
    for r in range(len(board)):#Iterate through entire board
        for c in range(len(board[0])):
            if (board[r][c] in blockers):#If the current tile is a blocking tile, it needs to be false. A light cannot be placed on an obstacle or number, or off the board.
                phi.add_clause([-1*abs(gridVariables[(r,c)])])#Set current tile to false-- no light on that tile.
#-----

#Print solutions 
    #for n in range ()
    phi.solve()#Solve the model, with all clauses having been added.
    print("Solutions, if any, print below this line:")
    print("-----------------------------------------")
    count = 0 #counts total number of models
    for s in phi.enum_models():#Iterates through all of the solutions(models) found by the SAT solver.
        for r in range(len(board)):#Iterate over board and print each tile.
            for c in range(len(board[0])):
                if(gridVariables[(r,c)] in s):#If the tile is "true" or positive in the model, place a light there. Lights are signified by 'O'. 
                    print("O",end="")
                else:
                    if (board[r][c] == 'X'): #Print out other tiles that are not lights.
                        print("X",end="")
                    elif (board[r][c] == '0'):
                        print("0",end="")
                    elif (board[r][c] == '1'):
                        print("1",end="")
                    elif (board[r][c] == '2'):
                        print("2",end="")
                    elif (board[r][c] == '3'):
                        print("3",end="")
                    elif (board[r][c] == '4'):
                        print("4",end="")
                    else:
                        print(".",end="")
            print() #Prints one model line by line
        print()#Prints multiple models
        count +=1 #number of models
    print("Total number of models: %d" %(count))

if __name__ == "__main__":
    main()