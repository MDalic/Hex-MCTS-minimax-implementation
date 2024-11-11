import time
import random
import copy
from treeNode import treeNode
from math import log, sqrt
from GameState import GameState


class MCTS():
    def __init__(self,playerNum,iterationLimit = None, timeLimit = None,explorationConstant=sqrt(2)):
        self.human = False
        self.explorationConstant = explorationConstant
        self.player = playerNum
        if iterationLimit == None and timeLimit == None:
            raise ValueError("MCTS requires a time or iteration limit")
        #iteration limit is chosen if both args are not none
        if timeLimit != None:
            self.limitType = 1  #time
            self.limit = timeLimit
        if iterationLimit != None:
            self.limitType = 2  #iteration
            self.limit = iterationLimit

    def makeTurn(self,initialState):
        self.root = treeNode(initialState,None)
        if self.limitType == 1:  #time limit
            endTime = time.time() + self.limit
            while time.time() < endTime:
                self.executeRound()
        if self.limitType == 2:  #iteration limit
            for i in range(self.limit):
                if i%500==0:
                    print(i)
                self.executeRound()
        bestChild = self.getBestChildToMakeMoveWith(self.root)
        action=(action for action, node in self.root.children.items() if node is bestChild).__next__()
        print('MCTS: {0} {1}'.format(action[0]+1,action[1]+1))
        return initialState.makeMove(action[0],action[1],self.player)
    
    def executeRound(self):
        node = self.selectNode(self.root)
        #state = copy.deepcopy(node.state)
        state = GameState(node.state.size)
        state.copy(node.state.replay)
        while state.isGameOver() == False:
            action = random.choice(state.availableMoves)
            state.makeMove(action[0],action[1],state.currentPlayer)
        if state.isGameOver() == self.player:
            reward = 1
        else:
            reward = 0
        self.backpropagate(node,reward)
    
    def backpropagate(self,node,reward):
        while node is not None:
            node.visited = node.visited + 1
            node.reward = node.reward + reward
            node = node.parent
    
    def selectNode(self,node):
        while node.state.isGameOver() == False:
            if node.isFullyExpanded():
                node = self.getBestChild(node)
            else:
                return self.expand(node)
        return node
    
    def expand(self,node):
        actions = node.state.availableMoves
        while len(actions)>0:
            action = random.choice(actions)
            if action not in node.children.keys():
                #nodeState = copy.deepcopy(node.state)
                nodeState = GameState(node.state.size)
                nodeState.copy(node.state.replay)
                nodeState.makeMove(action[0],action[1],nodeState.currentPlayer)
                newNode = treeNode(nodeState,node)
                node.children[action] = newNode
                return newNode

    def getBestChild(self,node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            #UCT = winrate + C * sqrt(ln(Nparent)/Nchild)
            if child.state.currentPlayer == self.player:
                nodeValue = -(child.reward / child.visited) + self.explorationConstant * sqrt(log(node.visited)/child.visited)
            else:
                nodeValue = child.reward / child.visited + self.explorationConstant * sqrt(log(node.visited)/child.visited)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    
    def getBestChildToMakeMoveWith(self,node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.reward / child.visited
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)