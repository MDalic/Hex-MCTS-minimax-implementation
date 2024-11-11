class TranspositionalTable:
    def __init__(self):
        self.table = {}

    def store(self,key,entry):
        if key in self.table:
            if entry.depth>self.table[key].depth:
                self.table[key] = entry
        else:
            self.table[key] = entry
        
    def lookUp(self,key):
        if key in self.table:
            entry = self.table[key]
            return entry
        return None
    
class TableEntry:
    def __init__(self,depth,score,bestMove,nodeType):
        self.depth = depth
        self.score = score
        self.bestMove = bestMove
        self.nodeType = nodeType
    
    def __str__(self):
        returnDict = {
            "depth":self.depth,
            "score":self.score,
            "bestMove":self.bestMove,
            "nodeType":self.nodeType
        }
        return str(returnDict)