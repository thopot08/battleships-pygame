class Tile:
    def __init__(self, position):
        self.position = position # position will be (x, y) but is accessed through (column, row) in the board class therefore it would be grid[y][x]
        self.occupyingShip = None
        self.targeted = False
        self.colour = "#6C7A89"
        
    def getShip(self):
        return self.occupyingShip
        
    def containsShip(self):
        return self.occupyingShip is not None

    def isTargeted(self):
        return self.targeted
