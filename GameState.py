from disjoint_set import DisjointSet
from colorama import Fore, Style
import numpy 

class GameState:
    def __init__(self,size):
        self.replay = []
        self.currentPlayer = 1
        self.size = size
        self.board = [[0 for i in range(self.size)] for j in range(self.size)]
        self.availableMoves = [(i,j) for i in range(self.size) for j in range(self.size)]
        self.availableMoves = self.sortMovesSpiral(self.availableMoves,self.size)
        self.allMoves = [(i,j) for i in range(self.size) for j in range(self.size)]
        self.maxAvailableMoves = len(self.allMoves)
        self.up = (-1,0)
        self.down = (self.size,0)
        self.left = (0,-1)
        self.right = (0,self.size)
        self.player1WinConditionSet = DisjointSet(self.availableMoves + [self.up, self.down])
        self.player2WinConditionSet = DisjointSet(self.availableMoves + [self.left,self.right])
        self.zobristArray = numpy.random.randint(0,2**64,size=(self.size*self.size,2),dtype=numpy.uint64)
        self.hash = self.calculateZobristHash()
        for i in range(self.size):
            self.player1WinConditionSet.union((0,i),self.up)
            self.player1WinConditionSet.union((self.size-1,i),self.down)
            self.player2WinConditionSet.union((i,0),self.left)
            self.player2WinConditionSet.union((i,self.size-1),self.right)


    def copy(self,replay):
        for replayMove in replay:
            self.makeMove(replayMove[0][0],replayMove[0][1],replayMove[1])


    def hexDistance(self,x, y, centerX, centerY):
        return (abs(x - centerX) + abs(y - centerY) + abs((x - centerX) + (y - centerY))) // 2

    def sortMovesSpiral(self,moves, size):
        centerX, centerY = size // 2, size // 2
        sortedMoves = sorted(moves, key=lambda coord: self.hexDistance(coord[0], coord[1], centerX, centerY))
        return sortedMoves

    def pushMoveToFront(self,move):
        if move in self.availableMoves:
            self.availableMoves.remove(move)
            self.availableMoves.insert(0,move)
            return True
        else:
            return False
    
    def __str__(self):
        returnText = Fore.BLUE+"|"+Style.RESET_ALL+Fore.RED+"-"*self.size*2+"\n "+Style.RESET_ALL
        i = 1
        for line in self.board:
            for cell in line:
                    if cell == 1:
                        stringValueOfCell = Fore.RED + "⬡" + Style.RESET_ALL
                    if cell == 2:
                        stringValueOfCell = Fore.BLUE + "⬡" + Style.RESET_ALL
                    if cell == 0:
                        stringValueOfCell = "⬡"
                    returnText = returnText + stringValueOfCell + " "
                    #returnText = returnText + str(cell) + " " 

            returnText = returnText + "\n" + Fore.BLUE+"|"+Style.RESET_ALL+" "*i
            i = i + 1
        returnText = returnText +"\n"+Fore.RED+"-"*self.size*4+Style.RESET_ALL
        return returnText
    
    def calculateZobristHash(self):
        hashValue = numpy.uint(0)
        for i in range(self.size):
            for j in range(self.size):
                if self.board[j][i] == 0:
                    continue
                hashValue ^= self.zobristArray[j * self.size + i,self.board[j][i]-1]
        return hashValue
    
    def updateZobristHash(self,i,j):
        self.hash ^= self.zobristArray[j * self.size + i,self.board[j][i]-1]

    
    def getNeighbours(self,x,y,player):
        neighbours = []
        for i,j in [(x+1,y),(x+1,y-1),(x,y+1),(x,y-1),(x-1,y),(x-1,y+1)]:
            if 0 <= i < self.size and 0 <= j < self.size and self.board[j][i]==player:
                neighbours.append((i,j))
        return neighbours
    
    def getNeighboursPlayerNeutral(self,x,y):
        neighbours = []
        for i,j in [(x+1,y),(x+1,y-1),(x,y+1),(x,y-1),(x-1,y),(x-1,y+1)]:
            if 0 <= i < self.size and 0 <= j < self.size:
                neighbours.append((i,j))
        return neighbours

    
    def makeMove(self,x,y,player):
        if player not in [1,2]:
            return False
        if (x,y) not in self.availableMoves:
            return False
        self.board[y][x] = player
        self.availableMoves.remove((x,y))
        self.updateZobristHash(x,y)
        neighbours = self.getNeighbours(x,y,player)
        for i,j in neighbours:
            if player == 1:
                self.player1WinConditionSet.union((j,i),(y,x))
            if player == 2:
                self.player2WinConditionSet.union((j,i),(y,x))
        self.currentPlayer = 3 - self.currentPlayer
        self.replay.append(((x,y),player))
        return True
    
    def undoMove(self,x,y):
        undoPlayer = self.board[y][x]
        self.updateZobristHash(x,y)
        self.board[y][x] = 0
        self.availableMoves.append((x,y))
        self.currentPlayer = 3 - undoPlayer

    def isGameOverFast(self):
        if self.player1WinConditionSet.find(self.up) == self.player1WinConditionSet.find(self.down):
            return 1
        if self.player2WinConditionSet.find(self.left) == self.player2WinConditionSet.find(self.right):
            return 2
        return False
    
    def isGameOver(self):
        player1WinConditionSet = DisjointSet(self.allMoves + [self.up, self.down])
        player2WinConditionSet = DisjointSet(self.allMoves + [self.left,self.right])
        for i in range(self.size):
            player1WinConditionSet.union((0,i),self.up)
            player1WinConditionSet.union((self.size-1,i),self.down)
            player2WinConditionSet.union((i,0),self.left)
            player2WinConditionSet.union((i,self.size-1),self.right)
        for move in self.allMoves:
            if self.board[move[0]][move[1]] == 1:
                neighbours = self.getNeighbours(move[1],move[0],1)
                for i,j in neighbours:
                    player1WinConditionSet.union((j,i),(move[0],move[1]))
            if self.board[move[0]][move[1]] == 2:
                neighbours = self.getNeighbours(move[1],move[0],2)
                for i,j in neighbours:
                    player2WinConditionSet.union((j,i),(move[0],move[1]))
        if player1WinConditionSet.find(self.up) == player1WinConditionSet.find(self.down):
            return 1
        if player2WinConditionSet.find(self.left) == player2WinConditionSet.find(self.right):
            return 2
        return False
