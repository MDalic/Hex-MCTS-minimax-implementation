import re
import random
import copy
import time
import numpy as np
from TranspositionalTable import TranspositionalTable,TableEntry
from pushMoveToFront import pushMoveToFront
class Human():
    def __init__(self,playerNum):
        self.player = playerNum
        self.human = True
    def makeTurnUI(self, gameState, coords):
        x = None
        y = None
        i = 0
        for q in range(-(gameState.size//2), gameState.size-(gameState.size//2)):
            if q == coords[0]:
                x = i
            if q == coords[1]:
                y = i
            i = i+1
        if x == None or y == None:
            return False
        move = gameState.makeMove(x,y,self.player)
        return move
    def makeTurn(self,gameState):
        userInput = input("\ncoords\t")
        userInput = re.sub(r'[^0-9\s]', '', userInput)
        userInput = userInput.split()
        x = int(userInput[0]) - 1 
        y = int(userInput[1]) - 1
        return gameState.makeMove(x,y,self.player)

class AI():
    def __init__(self, playerNum, type, depthLimit = None, timeLimit = None):
        defaultAI = "random"
        self.timeOut = False
        self.human = False
        self.progress = 0
        self.transpositionTable = TranspositionalTable()
        self.player = playerNum
        self.type = type
        if depthLimit == None and timeLimit == None and type == "minimax":
            raise ValueError(" requires a time or iteration limit")
        # depth limit is chosen if both args are not none
        if timeLimit != None:
            self.startTime = None
            self.limitType = 1  # time
            self.limit = timeLimit
        if depthLimit != None:
            self.limitType = 2  # depth
            self.limit = depthLimit
        availableTypes = {
            "random": self.random,
            "minimax":self.initMiniMax
        }
        try:
            self.makeTurn = availableTypes[self.type]
        except:
            print("That type of AI isn't supported, player is going to be default ai("+defaultAI+")")
            self.type = availableTypes["random"]

    def random(self,gameState):
        indexOfMove = random.randrange(len(gameState.availableMoves))
        return gameState.makeMove(gameState.availableMoves[indexOfMove][0], gameState.availableMoves[indexOfMove][1], self.player)
    def timeLimitMinimax(self, gameState):
        depth = 1
        bestValue = None
        bestMove = None
        while True:
            print(depth)
            value, move = self.minimaxNEW(gameState, self.player, float("-inf"), float("inf"), depth, timelimitEnabled=True)
            if bestValue == None:
                bestValue = value
            if bestMove == None:
                bestMove = move
            if value is not None and move is not None:
                if time.time() - self.startTime > self.limit:
                    break
                else:
                    bestMove = move
                    bestValue = value
            if bestValue != None and (bestValue >= 10000000 or bestValue <= -10000000):
                break
            depth = depth + 1
            if depth > 150:# safety net
                break
        self.timeOut = False
        return bestValue, bestMove



    def initMiniMax(self, gameState):
        self.startTime = time.time()
        newGameState = copy.deepcopy(gameState)
        if self.limitType == 1: # time limit
            value,bestMove = self.timeLimitMinimax(newGameState)
        if self.limitType == 2: # depth limit
            value,bestMove = self.minimaxNEW(newGameState,self.player,float('-inf'),float("inf"),self.limit)
        print("value:\t" + str(value))
        print('minimax: {0} {1}'.format(bestMove[0]+1,bestMove[1]+1))
        self.progress = 0
        return gameState.makeMove(bestMove[0],bestMove[1],self.player)

    def newTTNodeBasedOnValue(self,bestMove,bestValue,alpha,beta,depth,gameState):
        if bestMove is not None:
            newNodeType = None
            if bestValue <= alpha:  # upper bound
                newNodeType = 1
            elif bestValue >= beta:  # lower bound
                newNodeType = 2
            else:
                newNodeType = 3  # exact
            newNode = TableEntry(depth, bestValue, bestMove, newNodeType)
            self.transpositionTable.store(gameState.hash, newNode)


    def minimaxNEW(self, gameState, player, alpha, beta, depth=4, timelimitEnabled=False):
        if self.timeOut == True:
            return None, None
        if self.progress % 1000 == 0:
            print(self.progress)
            if timelimitEnabled:
                currentTime = time.time()
                if currentTime - self.startTime >= self.limit:
                    self.timeOut = True
                    return None, None
        self.progress = self.progress + 1
        nodeAvailableMoves = copy.deepcopy(gameState.availableMoves)
        alphaCopy = alpha
        betaCopy = beta
        ttEntry = self.transpositionTable.lookUp(gameState.hash)
        if (ttEntry is not None) and (ttEntry.bestMove in gameState.availableMoves) and (ttEntry.depth >= depth):
            if ttEntry.nodeType == 1:# upper bound
                betaCopy = min(ttEntry.score,beta)
            if ttEntry.nodeType == 2:# lower bound
                alphaCopy = max(ttEntry.score,alpha)
            if ttEntry.nodeType == 3:# exact
                return ttEntry.score,ttEntry.bestMove
            pushMoveToFront(ttEntry.bestMove,nodeAvailableMoves)
            
        terminalState = gameState.isGameOver()
        if terminalState or depth == 0:  # mby wrong
            if (not terminalState) and (ttEntry is not None):
                return ttEntry.score, None
            score = self.evaluate(gameState)
            ttNode = TableEntry(depth, score, None, 3)
            self.transpositionTable.store(gameState.hash, ttNode)
            return score,None
        if player == self.player:
            bestValue = float('-inf')
            bestMove = None
            for move in nodeAvailableMoves:
                # hashGamestate = gameState.hash
                gameState.makeMove(move[0], move[1], player)
                value,_ = self.minimaxNEW(gameState,3-player,alphaCopy,betaCopy,depth-1,timelimitEnabled=timelimitEnabled)
                gameState.undoMove(move[0], move[1])
                # assert gameState.hash == hashGamestate
                if value == None:
                    break
                if value>bestValue:
                    bestMove = move
                    bestValue = value
                alphaCopy = max(alphaCopy,value)
                if betaCopy <= alphaCopy:
                    break
            self.newTTNodeBasedOnValue(bestMove,bestValue,alpha,beta,depth,gameState)
            return bestValue,bestMove
        if player == 3-self.player:
            bestValue = float('inf')
            bestMove = None
            for move in gameState.availableMoves:
                gameState.makeMove(move[0],move[1],player)
                value,_ = self.minimaxNEW(gameState,3-player,alphaCopy,betaCopy,depth-1,timelimitEnabled=timelimitEnabled)
                gameState.undoMove(move[0],move[1])
                if value == None:
                    break
                if value<bestValue:
                    bestMove = move
                    bestValue = value
                betaCopy = min(betaCopy,value)
                if betaCopy <= alphaCopy:
                    break
            self.newTTNodeBasedOnValue(bestMove,bestValue,alpha,beta,depth,gameState)
            return bestValue,bestMove


    def evaluate(self,gamestate):
        if gamestate.isGameOver() == self.player:
            return 1000000 + (len(gamestate.availableMoves)*100)
        if gamestate.isGameOver() == 3-self.player:
            return -1000000 - (len(gamestate.availableMoves)*100)
        score = 100 * (self.getScore(3-self.player,gamestate) - self.getScore(self.player,gamestate))
        return score
    
    def getScore(self,player,gamestate):
        scores = np.array([[1000 for i in range(gamestate.size)] for j in range(gamestate.size)])
        updated = np.array([[True for i in range(gamestate.size)] for j in range(gamestate.size)])
        if player == 1:
            alignment= (0,1)
        if player == 2:
            alignment = (1,0)
        for i in range(gamestate.size):
            newcoord = tuple([i * j for j in alignment])
            updated[newcoord] = False
            if gamestate.board[newcoord[0]][newcoord[1]] == player:
                scores[newcoord] = 0
            elif gamestate.board[newcoord[0]][newcoord[1]] == 0:
                scores[newcoord] = 1
            else:
                scores[newcoord] = 1000
        
        scores = self.dijsktraUpdate(player,gamestate,scores,updated)
        results = [scores[alignment[0] * i - 1 + alignment[0]][alignment[1]*i - 1 + alignment[1]] for i in range(gamestate.size)]
        bestResult = min(results)
        return bestResult
    
    def dijsktraUpdate(self,player,gameState,scores,updated):
        updating = True
        while updating: 
            updating = False
            for i, row in enumerate(scores):
                for j, point in enumerate(row):
                    if not updated[i][j]: 
                        neighborcoords = gameState.getNeighboursPlayerNeutral(i,j)
                        for neighborcoord in neighborcoords:
                            target_coord = tuple(neighborcoord)
                            path_cost = 1000
                            if gameState.board[target_coord[0]][target_coord[1]]==0:
                                path_cost = 1
                            elif gameState.board[target_coord[0]][target_coord[1]]==player:
                                path_cost = 0
                            
                            if scores[target_coord] > scores[i][j] + path_cost:
                                scores[target_coord] = scores[i][j] + path_cost
                                updated[target_coord] = False
                                updating = True
        return scores

