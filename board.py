import tile
import ship

SHIP_LENGTHS = [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]

class Board:
    def __init__(self, width, height):
        self.grid = self.generateBoard(width, height)
        self.ships = self.generateShips()
        self.sunkenShips = []

    def checkLost(self):
        #if 1 == len(self.sunkenShips):
        if len(self.ships) == len(self.sunkenShips):
            return True
        else:
            return False

    def getTileFromPosition(self, position):
        xPos = position[0]
        yPos = position[1]
        return self.grid[yPos][xPos]
        
    def hitTile(self, targetPosition): # Must loop if -1 is returned
        if not(-1 < targetPosition[0] < 9 and -1 < targetPosition[1] < 9):
            print(f"Invalid position, {targetPosition}")
            return False

        targetTile = self.getTileFromPosition(targetPosition)
        tileTargeted = targetTile.isTargeted()
        if tileTargeted:
            print(f"Tile already hit, {targetPosition}")
            return False # The tile has already been targeted, therefore invalid
        else:
            targetTile.targeted = True
            tileHasShip = targetTile.containsShip()
            if tileHasShip:
                targetShip = targetTile.getShip()
                targetShip.registerHit(targetPosition)
                if targetShip.checkSunk():
                    self.sunkenShips.append(targetShip)
                    return True
    
    def placeShip(self, shipObject, shipPositions):
        # Validation Checking
        errored = False

        if len(shipPositions) != shipObject.length:
            print(f"Number of positions provided don't match, {len(shipPositions)} coordinates provided for ship of length {shipObject.length}")
            errored = True

        for position in shipPositions:
            if not(-1 < position[0] < 10 and -1 < position[1] < 10):
                print(f"Error, attempting to place ship outside of board limits. Position: {position}")
                errored = True
            else:
                tileObject = self.getTileFromPosition(position)
                if tileObject.containsShip():
                    print(f"Error, attempting to place ship with on a tile that is already occupied. Position: {position}")
                    errored = True
                    
        # Now that it is validated, place the ship
        if not errored:
            for position in shipPositions:
                tileObject = self.getTileFromPosition(position)
                tileObject.occupyingShip = shipObject
            shipObject.occupiedTiles = shipPositions
                
    def generateBoard(self, width, height): # Makes 2D Array of Tiles
        grid = []
        for rowNum in range(height):
            row = []
            for columnNum in range(width):
                position = (columnNum, rowNum)
                tileObject = tile.Tile(position)
                row.append(tileObject)
            grid.append(row)
        return grid
        
    def generateShips(self):
        ships = []
        for length in SHIP_LENGTHS:
            shipObject = ship.Ship(length)
            ships.append(shipObject)
        return ships
        
    def printBoard(self): # For developer debugging purposes
        for row in self.grid:
            for tileObject in row:
                if tileObject.containsShip():
                    shipObject = tileObject.getShip()
                    shipIndex = self.ships.index(shipObject)

                    if shipObject.checkSunk():
                        print(f"\033[31m{chr(shipIndex + 65)}\033[0m ", end="")
                    elif tileObject.isTargeted():
                        print(f"\033[33m{chr(shipIndex + 65)}\033[0m ", end="")
                    else:
                        print(f"\033[34m{chr(shipIndex + 65)}\033[0m ", end="")
                else:
                    if tileObject.isTargeted():
                        print("\033[33m0\033[0m ", end="")
                    else:
                        print("0 ", end="")
            print()
        print()