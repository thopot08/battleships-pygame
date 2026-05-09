import board as boardClass
import random

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

class Player:
    def __init__(self, playerId):
        self.id = playerId
        self.name = "placeholder"  # String name to display on GUIs
        self.ownedskins = []
        self.currency = 0
        self.board = boardClass.Board(9,9)
        self.fleetPlaced = False
        self.selectedWeapon = None

        self.weapons = {
            "missile" : 10,
            "torpedo" : 10,
            "cluster" : 10,
            "nuke" : 10
        }

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
        self.board = boardClass.Board(9,9)

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
