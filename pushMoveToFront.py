def pushMoveToFront(move,moveList):
    if move in moveList:
        moveList.remove(move)
        moveList.insert(0,move)
        return moveList
    else:
        return moveList