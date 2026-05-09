import random

weaponsMap = {
    "missile" : [
                 [0,-1],
        [-1, 0], [0, 0], [1, 0],
                 [0, 1]
    ],
    
    "nuke" : [
                          [0,-2],
                 [-1,-1], [0,-1], [1,-1],
        [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0],
                 [-1, 1], [0, 1], [1, 1],
                          [0, 2]
    ]
}

def useMissile(board, targetPosition):
    positions = []
    for positionVector in weaponsMap["missile"]:
        newX = targetPosition[0] + positionVector[0]
        newY = targetPosition[1] + positionVector[1]
        
        if -1 < newX < 9 and -1 < newY < 9:
            targetTile = board.getTileFromPosition((newX, newY))
            if not targetTile.isTargeted():
                positions.append((newX, newY))
    return positions
                
def useNuke(board, targetPosition):
    positions = []
    for positionVector in weaponsMap["nuke"]:
        newX = targetPosition[0] + positionVector[0]
        newY = targetPosition[1] + positionVector[1]
        
        if -1 < newX < 9 and -1 < newY < 9:
            targetTile = board.getTileFromPosition((newX, newY))
            if not targetTile.isTargeted():
                positions.append((newX, newY))
    return positions

def useTorpedo(board, targetPosition):
    positions = targetPosition
    targetTile = board.getTileFromPosition(targetPosition)
    if targetTile.containsShip():
        targetShip = targetTile.getShip()
        if len(targetShip.sunkenTiles) == 0:
            positions = targetShip.occupiedTiles
            print("ship found")
    return positions

def useCluster(board, targetPosition):
    positions = []
    for i in range(25):
        newX = random.randint(targetPosition[0] - 2, targetPosition[0] + 2)
        newY = random.randint(targetPosition[0] - 2, targetPosition[0] + 2)
        if -1 < newX < 9 and -1 < newY < 9:
            targetTile = board.getTileFromPosition((newX, newY))
            if not targetTile.isTargeted():
                positions.append((newX, newY))
        if len(positions) == 4:
          break
    return positions