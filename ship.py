class Ship:
    def __init__(self, length):
        self.length = length
        self.occupiedTiles = None
        self.sunkenTiles = []
        self.sunk = False
        
    def registerHit(self, targetPosition):
        self.sunkenTiles.append(targetPosition) # Marks the appropriate tile as sunk
    def checkSunk(self):
        if len(self.sunkenTiles) == len(self.occupiedTiles): # Checks if all ship tiles are in sunk array
            self.sunk = True
        return self.sunk