class treeNode():
    def __init__(self,gameState,parent):
        self.state = gameState
        self.parent = parent
        self.visited = 0
        self.reward = 0
        self.children = {}

    def isFullyExpanded(self):
        return len(self.state.availableMoves)==len(self.children)
    

    def __str__(self):
        returnDict = {
            "state":self.state.currentPlayer,
            "parent":self.parent,
            "visited":self.visited,
            "reward":self.reward,
            "parent":self.parent
        }
        return str(returnDict)
