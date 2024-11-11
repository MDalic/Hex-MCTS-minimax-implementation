from GameState import GameState
from MCTS import MCTS
from players import AI
from math import sqrt
import sys
MAX_OPTIONS = 5
MAX_OPTIONS_EXPLORATION_CONST = 4
def checkNumeric(x):
    if not isinstance(x, (int, float, complex)):
        raise ValueError('{0} is not numeric'.format(x))
def explorationConstantPicker():
    option = None
    exploConstants = [sqrt(2),0.5,0.2,0.1]
    print("Pick exploration Constant:\n1. sqrt(2)\n2. 0.5\n3. 0.2\n4. 0.1")
    try:
        while not isinstance(option,int):
            option = int(input())
    except:
        pass
    return exploConstants[option-1]

def playerIniter(optionSelected,playerNum):
    player = None
    if optionSelected == 1:#mcts time limited
        timeLimit = None
        explorationConstant = None
        while not isinstance(timeLimit,int):
            try:
                print("Input time limit in seconds")
                timeLimit = int(input())
                print(timeLimit)
            except:
                pass
        explorationConstant = explorationConstantPicker()
        player = MCTS(playerNum,timeLimit=timeLimit,explorationConstant=explorationConstant)
    if optionSelected == 2:# MCTS iteration limited
        iterationLimit = None
        explorationConstant = None
        while not isinstance(iterationLimit,int):
            try:
                print("Input iteration limit")
                iterationLimit = int(input())
                print(iterationLimit)
            except:
                pass
        explorationConstant = explorationConstantPicker()
        player = MCTS(playerNum,iterationLimit=iterationLimit,explorationConstant=explorationConstant)
    if optionSelected == 3:#Minimax time limited
        timeLimit = None
        while not isinstance(timeLimit,int):
            try:
                print("input time limit in seconds")
                timeLimit = int(input())
                print(timeLimit)

            except:
                pass
        player = AI(playerNum,"minimax",timeLimit=timeLimit)
    if optionSelected == 4:#Minimax depth limited
        depthLimit = None
        while not isinstance(depthLimit,int):
            try:
                print("input depth limit")
                depthLimit = int(input())
                print(depthLimit)
            except:
                pass
        player = AI(playerNum,"minimax",depthLimit=depthLimit)
    if optionSelected == 5:#Random moves
        player = AI(playerNum,"random")
    return player
    
def main():
    try:
        boardSize = int(sys.argv[1])
        gamesToPlay = int(sys.argv[2])
        if boardSize > 19:
            boardSize = 19
        if boardSize < 5:
            boardSize = 5
    except (ValueError,IndexError):
        print("size of board is not an integer")
        exit()
    optionP1 = -1
    optionP2 = -1

    print("Select player 1:\n1. MCTS time limited\n2. MCTS iteration limited\n3. Minimax time limited\n4. Minimax depth limited\n5. Random moves")
    while optionP1 <1 or optionP1 > MAX_OPTIONS:
        try:
            optionP1 = int(input())
        except:
            continue
    print("Select player 2:\n1. MCTS time limited\n2. MCTS iteration limited\n3. Minimax time limited\n4. Minimax depth limited\n5. Random moves")
    while optionP2 <1 or optionP2 > MAX_OPTIONS:
        try:
            optionP2 = int(input())
        except:
            continue


    players = [None,None]
    print("Pick options for Player1")
    players[0] = playerIniter(optionP1,1)
    print("Pick options for Player2")
    players[1] = playerIniter(optionP2,2)
    gameResults = []
    playersMove = 0
    for i in range(gamesToPlay):
        gameState = GameState(boardSize)
        while gameState.isGameOver()==False:
            if players[playersMove].makeTurn(gameState):
                playersMove = (playersMove+1)%2
        winner = gameState.isGameOver()
        gameResults.append(winner)
    playerWins = [0,0]
    for games in gameResults:
        playerWins[games-1] = playerWins[games-1] + 1 

    print(gameResults)
    print("player 1 winrate:"+str(int((playerWins[0]/gamesToPlay)*100))+"%")
    print("player 2 winrate:"+str(int((playerWins[1]/gamesToPlay)*100))+"%")

if __name__ == "__main__":
    main()
