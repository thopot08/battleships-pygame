from random import randint
from random import choice
import random
import board as boardClass

movement = {
    "down": [0, 1],
    "up": [0, -1],
    "right": [1, 0],
    "left": [-1, 0]
}

weaponsChance = {
    "missile" : 40,
    "torpedo" : 70,
    "cluster" : 90,
    "nuke" : 100
}


class Computer:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.name = "comp boy"
        self.board = boardClass.Board(9, 9)
        self.previousCoord = None
        self.weightedCoord = None
        self.priority = None # Contains [(xPos, yPos), direction]
        self.fleetPlaced = False
        self.selectedWeapon = None

        self.weapons = {
            "missile" : 1,
            "torpedo" : 0,
            "cluster" : 0,
            "nuke" : 0
        }
        
    def chooseTile(self,opponent):
        match self.difficulty:
            case "easy":
                return self.chooseTileEasy(opponent)
            case "medium":
                return self.chooseTileMedium(opponent)
            case "hard":
                return self.chooseTileHard(opponent)

    def giveWeapon(self):
        randomNumber = random.randint(1, 100)
        reward = "missile"
        for weapon, chance in weaponsChance.items():
            if randomNumber < chance:
                reward = weapon
                self.weapons[reward] += 1
                return reward
    
    def clearBoard(self):
        self.fleetPlaced = False
        for i in range(len(self.board.grid)):
            for j in range(len(self.board.grid[i])):
                self.board.grid[i][j].occupyingShip = None

    def automaticPlacement(self):
        self.clearBoard()
        for ship in self.board.ships:
            randomPosition = [random.randint(0, 8), random.randint(0, 8)]
            while self.board.getTileFromPosition(randomPosition).containsShip():
                randomPosition = [random.randint(0, 8), random.randint(0, 8)]

            placed = False
            tried_directions = []
            tiles_list = []

            while not placed:
                if len(tried_directions) == 4:
                    randomPosition = [random.randint(0, 8), random.randint(0, 8)]
                    while self.board.getTileFromPosition(randomPosition).containsShip():
                        randomPosition = [random.randint(0, 8), random.randint(0, 8)]
                    tried_directions = []
                    tiles_list = []

                randDirection = random.choice(list(movement.keys()))
                while randDirection in tried_directions:
                    randDirection = random.choice(list(movement.keys()))

                # print(randomPosition, randDirection)

                for tileNum in range(ship.length):
                    direction = movement[randDirection]
                    xPos = randomPosition[0]
                    xDir = direction[0]
                    yPos = randomPosition[1]
                    yDir = direction[1]

                    nextPosition = [xPos + tileNum * xDir, yPos + tileNum * yDir]
                    # print("tileNum", tileNum + 1, "of", ship.length, nextPosition)
                    if nextPosition[0] < 0 or nextPosition[0] > 8 or nextPosition[1] < 0 or nextPosition[1] > 8:
                        # print("reset case 1")
                        randomPosition = [random.randint(0, 8), random.randint(0, 8)]
                        tried_directions.append(randDirection)
                        tiles_list = []
                        break
                    else:
                        nextTile = self.board.getTileFromPosition(nextPosition)
                        if nextTile.containsShip():
                            # print("reset case 2")
                            tried_directions.append(randDirection)
                            tiles_list = []
                            break
                        else:
                            tiles_list.append(nextPosition)

                if len(tiles_list) == ship.length:
                    placed = True

            # print(tiles_list, "\n")
            self.board.placeShip(ship, tiles_list)
        self.fleetPlaced = True

    def chooseTileEasy(self, opponent):
        xPos, yPos = randint(0, 8), randint(0, 8)
        while opponent.board.getTileFromPosition((xPos, yPos)).isTargeted(): # Loop until new tile found
            xPos, yPos = randint(0, 8), randint(0, 8)
        self.previousCoord = (xPos, yPos)
        return (xPos, yPos)

    def chooseTileMedium(self, opponent):
        # This sections checks if the previous attack sunk the ship
        if self.previousCoord is not None:
            previousTile = opponent.board.getTileFromPosition(self.previousCoord)
            if previousTile.containsShip():
                tileShip = previousTile.getShip()
                if tileShip.checkSunk():
                    # If it has been sunk, reset weighted and priority to null to choose a new location to attack
                    self.weightedCoord, self.priority = None, None

        # Use chooseTileEasy for random coord if there are no weighted coordinates/priorities to go for
        if self.weightedCoord is None:
            targetPosition = self.chooseTileEasy(opponent)
            
            # If selected position was successful, save it as a weighted coordinate
            targetTile = opponent.board.getTileFromPosition(targetPosition)
            if targetTile.containsShip():
                self.weightedCoord = targetPosition
            self.previousCoord = targetPosition
            return targetPosition
        
        # If a WEIGHTED TILE has been hit, choose priority tiles
        elif self.priority is not None:
            direction = self.priority[1] # Index 0 contains position, Index 1 contains direction
            xPos = self.priority[0][0] # Previous attacked priority X position
            yPos = self.priority[0][1] # Previous attacked priority Y position
            
            # For each direction, it checks if the previous tile was a successful hit.
            # If it was a successful hit, then we want to continue going in that direction
            # If it was unsuccessful, we flip the direction it is going in as we know it must be opposite
            if direction == "left":
                if opponent.board.getTileFromPosition((xPos, yPos)).containsShip():
                    self.priority = ((xPos - 1, yPos), "left")
                else:
                    self.priority = ((xPos + 1, yPos), "right")
            elif direction == "right":
                if opponent.board.getTileFromPosition((xPos, yPos)).containsShip():
                    self.priority = ((xPos + 1, yPos), "right")
                else:
                    self.priority = ((xPos - 1, yPos), "left")
            # Up and down have negative to go up and positive to go down due to how 2D arrays are implemented
            elif direction == "up":
                if opponent.board.getTileFromPosition((xPos, yPos)).containsShip():
                    self.priority = ((xPos, yPos - 1), "up")
                else:
                    self.priority = ((xPos, yPos + 1), "down")
            elif direction == "down":
                if opponent.board.getTileFromPosition((xPos, yPos)).containsShip():
                    self.priority = ((xPos, yPos + 1), "down")
                else:
                    self.priority = ((xPos, yPos - 1), "up")
            self.previousCoord = self.priority[0]
            return self.priority[0]
                
        # If no priority tiles, then use the weighted coordinates to set new priorities
        else:
            xPos = self.weightedCoord[0]
            yPos = self.weightedCoord[1]
            
            directions = [
                ((xPos - 1, yPos), "left"),
                ((xPos + 1, yPos), "right"),
                ((xPos, yPos - 1), "up"),
                ((xPos, yPos + 1), "down")
                ]
            
            targetPosition, direction = choice(directions)
            while not(-1 < targetPosition[0] < 9 and -1 < targetPosition[1] < 9):
                targetPosition, direction = choice(directions)
            targetTile = opponent.board.getTileFromPosition(targetPosition)
            
            while targetTile.isTargeted():
                targetPosition, direction = choice(directions)
                targetTile = opponent.board.getTileFromPosition(targetPosition)
                
            # Successful tile from weighted coordinate, therefore becomes priority
            if targetTile.containsShip():
                self.priority = (targetPosition, direction)
            
            self.previousCoord = targetPosition
            return targetPosition
    
    def chooseTileHard(self,opponent):
        if self.weightedCoord == None and self.priority == None: # CHEAT if no idea
            if random.randint(1,2) == 1: # 50% chance
                aliveShips = []
                # fetch all of opponents alive ships
                for shipObject in opponent.board.ships:
                    if shipObject not in opponent.board.sunkenShips: # Check that the ship is not sunk
                        aliveShips.append(shipObject) # add to list of alive ships
                randomShip = choice(aliveShips) # choose random ship from list
                randomCoord = choice(randomShip.occupiedTiles) # select random coordinate from the random ship

                # set weighted and previous coord to the ship coordinate so that the medium AI can take over after the guaranteed ship hit
                self.weightedCoord = randomCoord
                self.previousCoord = randomCoord
                return randomCoord
              
            else:
                return self.chooseTileMedium(opponent) # If 50% chance fails
        else:
            return self.chooseTileMedium(opponent)
