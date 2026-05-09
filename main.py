import pygame, sys, random, threading
from pdatahandler import *
import player as playerClass
import computer as computerClass
import ship as shipClass
import weapons as weaponsClass

pygame.init()

# variables n stuff
tilesize = 30
gridsize = 10


class Gamble:
    def __init__(self):
        self.activePlayer = "p1"
        self.currency = 0
        self.betsize = 100

    def updateMoney(self):
        self.currency = int(fetchData(f"{self.activePlayer}currency"))

    def confirm(self):
        self.updateMoney()
        if self.betsize > self.currency:
            centeredMessage("you dont have enough money", (255, 20, 20), 450, 450, font)
            pygame.display.update()
            pygame.time.wait(1000)
            return  # Kill function

        spins = ["apple", "cherry", "orange", "banana", "pineapple", "grapes", "watermelon"]
        Slot1 = random.choice(spins)
        Slot2 = random.choice(spins)
        Slot3 = random.choice(spins)

        # rolling animation
        slots = [Slot1, Slot2, Slot3]
        for slotNum in range(3): # counts through the 3 slots
            for tickNum in range(16): # 15 random ticks to make spinning animation
                if tickNum != 15:
                    pygame.draw.rect(screen, (47, 89, 114), (90 + (slotNum * 260), 290, 200, 260))
                    centeredMessage(random.choice(spins), (255, 255, 255), 190 + (slotNum * 260), 420, font)
                else:
                    pygame.draw.rect(screen, (47, 89, 114), (90 + (slotNum * 260), 290, 200, 260))
                    centeredMessage(slots[slotNum], (255, 255, 255), 190 + (slotNum * 260), 420, font)
                pygame.display.update()
                pygame.time.wait(50)

        if self.currency >= self.betsize:
            if Slot1 == Slot2 and Slot2 == Slot3:
                changeMoney(self.activePlayer, self.betsize*10 - self.betsize)
                centeredMessage("you win!!!!", (255, 255, 255), 450, 250, font)
                centeredMessage("total profit:", (255, 255, 255), 450, 280, font)
                centeredMessage(f"£{self.betsize*10 - self.betsize}", (0, 255, 0), 450, 310, font)
                pygame.display.update()
                pygame.time.wait(2000)

            else:
                anyMatches = False
                for slotNum in range(len(slots)):
                    # Count if there are any matches of 2 slots
                    count = 0
                    for slot in slots:
                        if slots[slotNum] == slot:
                            count += 1
                    if count >= 2:
                        anyMatches = True

                if anyMatches:
                    changeMoney(self.activePlayer, self.betsize*3)
                    centeredMessage("you KINDA win!", (255, 255, 255), 450, 250, font)
                    centeredMessage("total profit:", (255, 255, 255), 450, 280, font)
                    centeredMessage(f"£{self.betsize*3}", (0, 255, 0), 450, 310, font)
                    pygame.display.update()
                    pygame.time.wait(2000)
                else:
                    changeMoney(self.activePlayer, - self.betsize)
                    centeredMessage("you lose :(", (255, 255, 255), 450, 250, font)
                    centeredMessage("total unprofit:", (255, 255, 255), 450, 280, font)
                    centeredMessage(f"£{-self.betsize}", (255,0,0), 450, 310, font)
                    pygame.display.update()
                    pygame.time.wait(2000)

        self.updateMoney()
        updatePlayer(self.activePlayer)

    def changePlayer(self):
        print("working")
        if self.activePlayer == "p1":
            self.activePlayer = "p2"
        elif self.activePlayer == "p2":
            self.activePlayer = "p3"
        elif self.activePlayer == "p3":
            self.activePlayer = "p4"
        elif self.activePlayer == "p4":
            self.activePlayer = "p1"
        self.betsize = 100
        updatePlayer(self.activePlayer)

    def increaseBetSize(self):
        self.betsize += 100

    def decreaseBetSize(self):
        if self.betsize > 0:
            self.betsize -= 100
        else:
            centeredMessage("sorry you cant bet a negative amount", (255, 0, 0), 450, 450, font)
            pygame.display.update()
            pygame.time.wait(1000)

    def allIN(self):
        self.betsize = int(fetchData(f"{self.activePlayer}currency"))

    def resetBetSize(self):
        self.betsize = 100


gamble = Gamble()

WIDTH = 900
HEIGHT = 900
titleFont = pygame.font.SysFont("comic sans", 70)
font = pygame.font.SysFont("comic sans", 20)
clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Better Battleships")


p1 = playerClass.Player("p1")
p2 = playerClass.Player("p2")
p3 = playerClass.Player("p3")
p4 = playerClass.Player("p4")

players = [p1, p2, p3, p4]
computer = []
activePlayer = p1
targetPlayer = p2
selectedTile = None
winner = "placeholder"

# --- Pygame classes ---

class Button:  # button for the pygame menu buttons tingy
    def __init__(self, x, y, sizex, sizey, colour, text="", chosenfont=font, textcolour=(255, 255, 255),
                 connectedMenu=None, connectedButtons=[], active=False, function=None):
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.colour = colour
        self.text = text
        self.chosenfont = chosenfont
        self.textcolour = textcolour
        self.connectedMenu = connectedMenu
        self.connectedButtons = connectedButtons  # this holds the menus/buttons that a button will reveal
        self.active = active
        self.function = function

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, self.colour, (self.x, self.y, self.sizex, self.sizey))
            # draw text
            centeredMessage(self.text, self.textcolour, self.x + (self.sizex / 2), self.y + (self.sizey / 2),
                            self.chosenfont)

    def pressed(self, mousex, mousey):  # check if button is clicked
        if mousex > self.x and mousex < self.sizex + self.x and mousey > self.y and mousey < self.sizey + self.y and self.active:
            if self.connectedMenu != None:
                global activeMenu
                activeMenu = self.connectedMenu

            for button in self.connectedButtons:
                if button.active:
                    button.active = False
                else:
                    button.active = True
            if self.function != None:
                self.function()  # function is called, if attribute left empty nothing happens


class Menu:
    def __init__(self, bgColour):
        self.bgColour = bgColour
        self.buttons = []

    def addButtons(self, buttons):
        for b in buttons:
            self.buttons.append(b)

    def draw(self):
        screen.fill(self.bgColour)
        for button in self.buttons:
            button.draw()


def centeredMessage(txt, colour, x, y,chosenfont):
    textsurface = chosenfont.render(txt, True, colour)
    textrect = textsurface.get_rect()
    textrect.center = x, y
    screen.blit(textsurface, textrect)

def setPlayerCount(playercount):
    global players
    if playercount == 2:
        players = [p1,p2]
    if playercount == 3:
        players = [p1,p2,p3]
    if playercount == 4:
        players = [p1,p2,p3,p4]

def initialiseComputer(difficulty):
    global computer, targetPlayer
    computer = computerClass.Computer(difficulty)
    computer.automaticPlacement()
    computer.board.printBoard()

    global players
    players = [p1, computer]
    targetPlayer = computer

def switchActivePlayer():
    global activePlayer
    for plyrIndex in range(len(players)):
        if activePlayer == players[plyrIndex]:
            if plyrIndex == len(players) - 1:
                activePlayer = players[0]
            else:
                activePlayer = players[plyrIndex+1]
            break

def chooseWeapon(clickedWeapon):
    if activePlayer.weapons[clickedWeapon] > 0:
        if activePlayer.selectedWeapon == clickedWeapon:
            activePlayer.selectedWeapon = None
        else:
            activePlayer.selectedWeapon = clickedWeapon
    else:
        centeredMessage("YOU DONT HAVE THAT.", (0, 0, 0), 452, 452, titleFont)
        centeredMessage("YOU DONT HAVE THAT.", (255,0,0),450,450,titleFont)
        pygame.display.update()
        pygame.time.wait(1000)

def mainAutoPlace():
    global activePlayer
    activePlayer.automaticPlacement()

    # smallShip = activePlayer.board.ships[9]
    # shipPositions = [[0, 1], [0, 2]]
    # activePlayer.board.placeShip(smallShip, shipPositions)
    # activePlayer.fleetPlaced = True
  
def computerStrike(opponent):
    global selectedTile

    targetPosition = computer.chooseTile(opponent) # Choose tile using computer's selected algorithm
    selectedTile = [targetPosition[0],targetPosition[1]] # Set selectedTile to the computer's chosen tile

    pygame.draw.circle(screen, (255, 170, 0), ((selectedTile[0] * 60) + 65, (selectedTile[1] * 60) + 210), 20, 3) # Draw circle on the grid
    pygame.display.update() # update display to show the circle
    pygame.time.wait(300) # pause for 300 ms

    mainHitTile() # hit selected tile on opponents grid


def mainClearBoard():
    global activePlayer
    activePlayer.clearBoard()

def changeNextPlayer():
    global activePlayer, targetPlayer

    activeIndex = players.index(activePlayer)
    activePlayer = players[(activeIndex + 1) % len(players)]

    while activePlayer.board.checkLost(): # Keep repeating until player isnt dead
        activeIndex = players.index(activePlayer)
        activePlayer = players[(activeIndex + 1) % len(players)]
    # if the active becomes target, change target player
    if targetPlayer == activePlayer:
        targetIndex = players.index(targetPlayer)
        targetPlayer = players[(targetIndex + 1) % len(players)]

def winCheck():
    global activeMenu, winner
    count = 0
    for player in players:
        if not player.board.checkLost(): # if player hasn't lost
            count += 1

    if count == 1:
        for player in players:
            if not player.board.checkLost():
                if player != computer:
                    changeMoney(player.id, 1000)
                    updatePlayer(player.id)
                winner = player
                activeMenu = winMenu

def mainHitTile():
    global selectedTile
    if selectedTile is not None:
        targetedPositions = []

        if activePlayer.selectedWeapon:
            activePlayer.weapons[activePlayer.selectedWeapon] -= 1
            match activePlayer.selectedWeapon:
                case "missile":
                    positions = weaponsClass.useMissile(targetPlayer.board, selectedTile)
                    for position in positions:
                        targetPlayer.board.hitTile(position)
                        targetedPositions.append(position)
                case "torpedo":
                    positions = weaponsClass.useTorpedo(targetPlayer.board, selectedTile)
                    print(positions)
                    if type(positions[0]) == list:
                        for position in positions:
                            targetPlayer.board.hitTile(position)
                            targetedPositions.append(position)
                    else:
                        targetPlayer.board.hitTile(positions)
                        targetedPositions.append(positions)
                case "cluster":
                    positions = weaponsClass.useCluster(targetPlayer.board, selectedTile)
                    for position in positions:
                        targetPlayer.board.hitTile(position)
                        targetedPositions.append(position)
                case "nuke":
                    positions = weaponsClass.useNuke(targetPlayer.board, selectedTile)
                    for position in positions:
                        targetPlayer.board.hitTile(position)
                        targetedPositions.append(position)
        else:
            targetPlayer.board.hitTile(selectedTile)
            targetedPositions.append(selectedTile)
        numHits = 0
        for position in targetedPositions:
            targetTile = targetPlayer.board.getTileFromPosition(position)
            x = position[0] * 60 + 65
            y = position[1] * 60 + 210

            if targetTile.containsShip():
                numHits += 1
                pygame.draw.circle(screen, (100, 255, 100), (x, y), 10)

            else:
                pygame.draw.circle(screen, (255,255,0), (x,y), 5)

        #  chance to get weapon
        if targetTile.containsShip():
            if targetTile.getShip().checkSunk():
                randomChance = random.randint(0,1) # 0 = fail, 1 = get random weapon
                if randomChance == 1:
                    print(f"{activePlayer.name} got a {activePlayer.giveWeapon()}")

        if numHits > 0:
            centeredMessage("HIT!", (0, 0, 0), 743, 472, titleFont)
            centeredMessage("HIT!", (0, 255, 0), 743, 470, titleFont)
            if activePlayer.selectedWeapon is not None:
                activePlayer.selectedWeapon = None
                changeNextPlayer()
        else:
            centeredMessage("MISS", (0,0,0),743,472,titleFont)
            centeredMessage("MISS", (255, 0, 0), 743, 470, titleFont)
            if activePlayer.selectedWeapon is not None:
                activePlayer.selectedWeapon = None
            changeNextPlayer()

        centeredMessage(f"Next turn: {activePlayer.name}", (0,0,0),743,521,font)
        centeredMessage(f"Next turn: {activePlayer.name}", (255,255,255),743,520,font)

        pygame.display.update()
        pygame.time.wait(1500)

        selectedTile = None
        winCheck()

    else:
        centeredMessage("YOU HAVENT SELECTED A TILE", (0, 0, 0), 452, 452, font)
        centeredMessage("YOU HAVENT SELECTED A TILE", (255,0,0),450,450,font)
        pygame.display.update()
        pygame.time.wait(1000)


def setDefaultValues():
    global players, activePlayer, targetPlayer, selectedTile
    players = [p1,p2,p3,p4]
    for player in players:
        player.clearBoard()
        player.selectedWeapon = None
        player.weapons = {
            "missile":0,
            "torpedo":0,
            "cluster":0,
            "nuke":0
        }
    activePlayer = p1 # set active player to default
    targetPlayer = p2
    selectedTile = None

    print(activePlayer.id, targetPlayer.id)

def switchTarget(num):
    global targetPlayer, selectedTile

    if len(players) == 1:
        return
    targetIndex = players.index(targetPlayer)

    targetPlayer = players[(targetIndex + num) % len(players)]
    selectedTile = None # remove selected tile when switching board.
    #if targetPlayer == activePlayer:
        #targetPlayer = players[(targetIndex + 2 * num) % len(players)]


# Functions for creating menus
def createMainMenu():
    mainMenu = Menu((18, 58, 90))
    title = Button(10, 10, WIDTH - 20, 150, (47, 89, 114), "Better Battleships", titleFont, active=True)
    # player vs player
    twoP = Button(260, 210, 150, 150, (108, 122, 137), "2 player", active=False, function=lambda: setPlayerCount(2))
    threeP = Button(460, 210, 150, 150, (108, 122, 137), "3 player", active=False, function=lambda: setPlayerCount(3))
    fourP = Button(660, 210, 150, 150, (108, 122, 137), "4 player", active=False, function=lambda: setPlayerCount(4))
    pvp = Button(35, 200, 170, 170, (47, 89, 114), "player vs player", connectedButtons=[twoP, threeP, fourP],
                 active=True)
    mainMenu.addButtons([pvp, twoP, threeP, fourP, title])
    # player vs ai
    easyButton = Button(260, 410, 150, 150, (108, 122, 137), "Easy", active=False, function= lambda: initialiseComputer("easy"))
    mediumButton = Button(460, 410, 150, 150, (108, 122, 137), "Medium", active=False,  function=lambda: initialiseComputer("medium"))
    hardButton = Button(660, 410, 150, 150, (108, 122, 137), "Hard", active=False,  function=lambda: initialiseComputer("hard"))
    pvaButton = Button(35, 400, 170, 170, (47, 89, 114), "Player vs AI",
                       connectedButtons=[easyButton, mediumButton, hardButton], active=True)
    mainMenu.addButtons([pvaButton, easyButton, mediumButton, hardButton])
    # shop
    buyButton = Button(260, 610, 150, 150, (108, 122, 137), "Buy", connectedMenu=None, active=False)
    inventoryButton = Button(460, 610, 150, 150, (108, 122, 137), "Inventory", active=False)
    gambleButton = Button(660, 610, 150, 150, (108, 122, 137), "Gamble", active=False)
    shopButton = Button(35, 600, 170, 170, (47, 89, 114), "Shop",
                        connectedButtons=[buyButton, inventoryButton, gambleButton], active=True)
    mainMenu.addButtons([shopButton, buyButton, inventoryButton, gambleButton])

    return mainMenu
mainMenu = createMainMenu()


def createShopMenu():
    shopMenu = Menu((18, 58, 90))
    title = Button(10, 10, WIDTH - 20, 150, (47, 89, 114), "Buy Menu", titleFont, active=True)
    backButton = Button(10, 170, 40, 40, (47, 89, 114), "<--", connectedMenu=mainMenu, active=True,function=setDefaultValues)
    skinBackground = Button(10, 220, 430, 550, (47, 89, 114), active=True)
    preview = Button(460, 220, 150, 40, (47, 89, 114), "preview", active=True)
    previewBackground = Button(460, 260, 430, 510, (47, 89, 114), active=True)
    previewBackground2 = Button(470, 270, 410, 490, (18, 58, 90), active=True)
    previewBackground3 = Button(480, 280, 390, 370, (47, 89, 114), active=True)
    confirm = Button(480, 670, 390, 80, (47, 89, 114), "Confirm", active=True)
    currency = Button(645, 175, 245, 60, (47, 89, 114), active=True)
    player = Button(95, 170, 250, 40, (47, 89, 114), "player:", active=True)
    changeplayer = Button(355, 170, 250, 40, (47, 89, 114), "Change player", active=True)
    shopMenu.addButtons([title, backButton, skinBackground, preview, previewBackground, currency, previewBackground2,
                         previewBackground3, confirm, player, changeplayer])

    return shopMenu
shopMenu = createShopMenu()


def createinventoryMenu():
    inventoryMenu = Menu((18, 58, 90))
    title = Button(10, 10, WIDTH - 20, 150, (47, 89, 114), "Inventory", titleFont, active=True)
    backButton = Button(10, 170, 40, 40, (47, 89, 114), "<--", connectedMenu=mainMenu, active=True,function=setDefaultValues)
    skinBackground = Button(10, 220, 430, 550, (47, 89, 114), active=True)
    preview = Button(460, 220, 150, 40, (47, 89, 114), "preview", active=True)
    previewBackground = Button(460, 260, 430, 510, (47, 89, 114), active=True)
    previewBackground2 = Button(470, 270, 410, 490, (18, 58, 90), active=True)
    previewBackground3 = Button(480, 280, 390, 370, (47, 89, 114), active=True)
    equip = Button(480, 670, 390, 80, (47, 89, 114), "Equip", active=True)
    player = Button(195, 170, 250, 40, (47, 89, 114), "player:", active=True)
    changeplayer = Button(455, 170, 250, 40, (47, 89, 114), "Change player", active=True)
    inventoryMenu.addButtons(
        [title, backButton, skinBackground, preview, previewBackground, previewBackground2, previewBackground3, equip,
         player, changeplayer])

    return inventoryMenu
inventoryMenu = createinventoryMenu()


def createSlotMachine():
    slotMachine = Menu((18, 58, 90))
    title = Button(10, 10, WIDTH - 20, 150, (47, 89, 114), "Slot Machine", titleFont, active=True)
    backButton = Button(10, 170, 40, 40, (47, 89, 114), "<--", connectedMenu=mainMenu, active=True,function=setDefaultValues)
    background = Button(10, 230, 880, 470, (47, 89, 114), active=True)
    background2 = Button(40, 260, 820, 410, (18, 58, 90), active=True)
    slot1 = Button(90, 290, 200, 260, (47, 89, 114), active=True)
    slot2 = Button(350, 290, 200, 260, (47, 89, 114), active=True)
    slot3 = Button(610, 290, 200, 260, (47, 89, 114), active=True)
    confirm = Button(10, 710, 390, 105, (47, 89, 114), "Confirm", active=True, function=gamble.confirm)
    increasebetsize = Button(410, 710, 235, 50, (47, 89, 114), "Increase betsize", active=True,
                             function=gamble.increaseBetSize)
    decreasebetsize = Button(655, 710, 235, 50, (47, 89, 114), "Decrease betsize", active=True,
                             function=gamble.decreaseBetSize)
    allInButton = Button(420, 770,215,45,(47,89,114),"ALL IN", font, (255,0,0),active=True, function=gamble.allIN)
    resetBet = Button(665,770, 215,45,(47,89,114),"Reset betsize",font,active=True, function=gamble.resetBetSize)
    betsize = Button(340, 580, 220, 50, (47, 89, 114), active=True)
    player = Button(95, 170, 250, 40, (47, 89, 114), active=True)
    changeplayer = Button(355, 170, 250, 40, (47, 89, 114), "Change player", active=True,function=gamble.changePlayer)
    currency = Button(645, 170, 245, 40, (47, 89, 114), active=True)
    slotMachine.addButtons(
        [title, backButton, background, background2, slot1, slot2, slot3, confirm, increasebetsize, decreasebetsize, allInButton,
         resetBet,betsize, player, changeplayer, currency])

    return slotMachine
slotMachine = createSlotMachine()

# ignore this i had to take it out of the gameplay menu BECAUse the grid was drawing on top of it. -------------------------------------------------
# i didnt want the grid to draw on top of it

# CE stands for confirm exit
CEbackground = Button(200, 300, 400, 250, (0, 40, 78), "Are you sure you want to exit?", font, (255, 255, 255))
CEtext = Button(200, 320, 400, 50, (0, 40, 78), "Exit game", titleFont, (220, 182, 57))  # this is the title
CEcancel = Button(240, 490, 150, 50, (79, 133, 166), "Cancel", font, (255, 255, 255),
                  connectedButtons=[CEbackground, CEtext])
CEconfirm = Button(410, 490, 150, 50, (79, 133, 166), "Confirm", font, (255, 255, 255),
                   connectedButtons=[CEbackground, CEtext, CEcancel], connectedMenu=mainMenu,function=setDefaultValues)
# Ensure cancel and confirm have each part of CE connected to them so the confirm exit menu disappears when clicked
CEcancel.connectedButtons.append(CEcancel)
CEcancel.connectedButtons.append(CEconfirm)
CEconfirm.connectedButtons.append(CEconfirm)
CEbuttons = [CEbackground,CEtext,CEcancel,CEconfirm]

def createGameplayMenu():
    global CEbackground, CEtext, CEcancel, CEconfirm
    gameplayMenu = Menu((18, 58, 90))
    playertxtbox = Button(10, 10, 650, 100, (47, 89, 114),"", font, active=True)
    playertimer = Button(670, 10, 220, 100, (47, 89, 114), "timer", font, active=True)

    currentboarddisplay = Button(633, 170, 220, 110, (47, 89, 114), active=True)
    attackingtxt = Button(633, 190, 220, 20, (47, 89, 114), "Current", font, active=True)
    attackingtxt2 = Button(633, 210, 220, 20, (47, 89, 114), "Board:", font, active=True)
    switchplrLeft = Button(638, 290, 100, 100, (47, 89, 114), "<", titleFont, active=True, function=lambda: switchTarget(-1))
    switchplrRight = Button(748, 290, 100, 100, (47, 89, 114), ">", titleFont, active=True, function=lambda: switchTarget(1))
    confirmAttack = Button(633,610,220,110,(47,89,114),"STRIKE!!!!!!", font, active=True, function=mainHitTile)

    gridBG = Button(25, 170, 560, 560, (108, 122, 137), active=True)
    grid = Button(35, 180, 540, 540, (47, 89, 114), active=True)

    gameplayMenu.addButtons(
        [playertxtbox, playertimer, currentboarddisplay, attackingtxt, attackingtxt2, switchplrLeft,
         switchplrRight,confirmAttack, gridBG, grid])

    # ABILITY buttons
    missileButton = Button(40,740,100,75,(47,89,114),"misile",font,active=True, function=lambda: chooseWeapon("missile"))
    torpedoButton = Button(185, 740, 100, 75, (47, 89, 114), "torpedo", font, active=True, function=lambda: chooseWeapon("torpedo"))
    clusterButton = Button(330, 740, 100, 75, (47, 89, 114), "cluster", font, active=True, function=lambda: chooseWeapon("cluster"))
    nukeButton    = Button(475, 740, 100, 75, (47, 89, 114), "NUKE", font, active=True, function=lambda: chooseWeapon("nuke"))
    gameplayMenu.addButtons([missileButton, torpedoButton, clusterButton, nukeButton])

    backButton = Button(10, 120, 40, 40, (47, 89, 114), "<--",
                        connectedButtons=[CEbackground, CEtext, CEcancel, CEconfirm], active=True)
    gameplayMenu.addButtons([backButton, CEbackground, CEtext, CEcancel, CEconfirm])

    return gameplayMenu
gameplayMenu = createGameplayMenu()

def checkFleetsPlaced():
    allFleetsPlaced = True
    for player in players:
        if player.fleetPlaced == False:
            allFleetsPlaced = False
            print(f"{player.name} has no fleets!")
    if allFleetsPlaced:
        global activeMenu, activePlayer
        activePlayer = p1
        activeMenu = gameplayMenu
    else:
        centeredMessage("SOMEONE hasn't placed their FLEETS!!!!!", (0,0,0),452,452,font) # black shadow
        centeredMessage("SOMEONE hasn't placed their FLEETS!!!!!", (255,0,0), 450,450,font)
        pygame.display.update()
        pygame.time.wait(1000)


def createFleetPlacementMenu():
    fleetPlacement = Menu((18, 58, 90))
    title = Button(10, 10, WIDTH - 20, 150, (47, 89, 114), "Fleet Placement", titleFont, active=True)
    backButton = Button(10, 170, 40, 40, (47, 89, 114), "<--", connectedMenu=mainMenu, active=True,function=setDefaultValues)

    gridBox = Button(20, 290, 450, 450, (47, 89, 114), active=True)
    autoPlacement = Button(10, 760, 470, 50, (47, 89, 114), "Automatic Placement", font, active=True, function=mainAutoPlace)
    switchPlayer = Button(490,640,390,50,(47, 89, 114), "Switch Player", font, active=True, function=switchActivePlayer)
    resetBoard = Button(490,700,390,50,(47,89,114),"Reset Board", font, active=True, function=mainClearBoard)
    confirmPlacement = Button(490, 760, 390, 50, (47, 89, 114), "Confirm Placement", font, active=True, function=checkFleetsPlaced)
    playertxtbox = Button(30, 230, 430, 50, (47, 89, 114),"", font, active=True)
    fleetPlacement.addButtons([title, backButton, gridBox, autoPlacement,switchPlayer, resetBoard, confirmPlacement, playertxtbox])
    return fleetPlacement
fleetPlacementMenu = createFleetPlacementMenu()


def createWinMenu():
    winMenu = Menu((18,58,90))
    winnerDisplay = Button(50,200,800,100,(47,89,114),"",active=True)
    backButton = Button(350, 500, 200, 50, (47,89,114), "Return to main menu", font, (255, 255, 255),active=True, connectedMenu=mainMenu,function=setDefaultValues)
    winMenu.addButtons([winnerDisplay,backButton])
    return winMenu
winMenu = createWinMenu()



for button in mainMenu.buttons:
    match button.text:
        case "Buy":
            button.connectedMenu = shopMenu
        case "Inventory":
            button.connectedMenu = inventoryMenu
        case "Gamble":
            button.connectedMenu = slotMachine
        case "Easy":
            button.connectedMenu = fleetPlacementMenu
        case "Medium":
            button.connectedMenu = fleetPlacementMenu
        case "Hard":
            button.connectedMenu = fleetPlacementMenu
        case "2 player":
            button.connectedMenu = fleetPlacementMenu
        case "3 player":
            button.connectedMenu = fleetPlacementMenu
        case "4 player":
            button.connectedMenu = fleetPlacementMenu


def updatePlayer(playerID):
    global activePlayer
    for player in players:
        if player.id == playerID:
            activePlayer = player
            activePlayer.name = fetchData(f"{activePlayer.id}name")
            activePlayer.ownedskins = fetchData(f"{activePlayer.id}ownedskins").split(",")
            activePlayer.currency = fetchData(f"{activePlayer.id}currency")


activeMenu = mainMenu  # by default mainmenu is the active menu

for player in players:
    updatePlayer(player.id)
activePlayer = p1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()

            for button in activeMenu.buttons:
                button.pressed(x, y)
            if activePlayer == computer:
                print("banana26statenet")
          
            elif activeMenu == gameplayMenu and 35 < x < 575 and 180 < y < 720 and activePlayer != targetPlayer and not targetPlayer.board.checkLost(): # Dimensions of the grid GUI
                # Convert positions to tile number (each tile = 60x60, offset = 35 and 180)
                x = int((x-35)/60)
                y = int((y-180)/60)
                # cant select tile if it was already hitted
                if not targetPlayer.board.getTileFromPosition((x,y)).isTargeted():
                    selectedTile = [x,y]
      
    activeMenu.draw()
    # bottom border
    pygame.draw.rect(screen, (14, 46, 71), (0, 825, WIDTH, 75))

    # Menu specific thingies:

    if activeMenu == fleetPlacementMenu:
        centeredMessage(f"{activePlayer.name} place your fleets", (255,255,255), 245,255, font)
        # draw grid
        #for i in range(10):
            #pygame.draw.line(screen, (255,255,255), (20+ i*50, 290), (20 + i*50, 740))
            #pygame.draw.line(screen,(255,255,255),(20, 290+i*50), (470, 290+i*50))
        for arrayy in range(9):
            y = 315 + arrayy * 50
            for arrayx in range(9):
                x = 45+arrayx*50
                if activePlayer.board.grid[arrayy][arrayx].containsShip():
                    # gradient colour thing
                    shipindex = activePlayer.board.ships.index(activePlayer.board.grid[arrayy][arrayx].getShip())
                    # gets lighter the higher ship index
                    shipcolour = (255, shipindex*15,shipindex*15)

                    pygame.draw.circle(screen, shipcolour, (x, y), 12)
                    #pygame.draw.rect(screen,shipcolour, (x-20, y-20, 45,45))
                else:
                    pygame.draw.circle(screen, (255,255,255), (x,y),5)

    elif activeMenu == gameplayMenu:
        # show ability count
        centeredMessage(str(activePlayer.weapons["missile"]), (255,255,255), 130,750, font)
        centeredMessage(str(activePlayer.weapons["torpedo"]), (255,255,255), 275,750, font)
        centeredMessage(str(activePlayer.weapons["cluster"]), (255,255,255), 420,750, font)
        centeredMessage(str(activePlayer.weapons["nuke"]), (255,255,255), 565,750, font)
        centeredMessage(f"Currently selected: {activePlayer.selectedWeapon}", (255,255,255),750, 777, font)

        if activePlayer == targetPlayer:
            centeredMessage("(",(255,255,255), 660,485, titleFont)
            centeredMessage("THIS IS YOUR",(255,255,255), 743,480, font)
            centeredMessage("OWN BOARD", (255, 255, 255), 743, 510, font)
            centeredMessage(")", (255, 255, 255), 825, 485, titleFont)

        centeredMessage(f"{activePlayer.name}'s turn", (255,255,255), 335,60,font)
        centeredMessage(targetPlayer.name,(255,255,255), 743,250 , font)
        for arrayy in range(9):
            y = 210 + arrayy * 60
            for arrayx in range(9):
                x = 65+arrayx*60

                targetTile = targetPlayer.board.getTileFromPosition((arrayx,arrayy))
                if targetTile.isTargeted() and targetTile.containsShip():
                    if targetTile.getShip().checkSunk():
                        shipindex = targetPlayer.board.ships.index(targetPlayer.board.grid[arrayy][arrayx].getShip())
                        shipcolour = (255, shipindex * 15, shipindex * 15)
                        pygame.draw.circle(screen, shipcolour, (x, y), 12)
                    else:
                        pygame.draw.circle(screen, (100, 255, 100), (x, y), 10)

                elif targetTile.isTargeted() and not targetTile.containsShip():
                    pygame.draw.circle(screen, (255, 255, 0), (x, y), 5)
                else:
                    pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)
                '''
                if targetPlayer.board.getTileFromPosition((arrayx,arrayy)).containsShip():
                    shipindex = targetPlayer.board.ships.index(targetPlayer.board.grid[arrayy][arrayx].getShip())
                    shipcolour = (255, shipindex * 15, shipindex * 15)
                    pygame.draw.circle(screen, shipcolour, (x, y), 12)
                '''
        # SHOW THAT DEAD PLAYER BOARD IS DEAD
        if targetPlayer.board.checkLost():
            pygame.draw.line(screen, (0,0,0), (20,165),(590,735),15)
            pygame.draw.line(screen, (0, 0, 0), (20, 735), (590, 165), 15)
            centeredMessage("(", (255, 255, 255), 700, 485, titleFont)
            centeredMessage(f"{targetPlayer.name}", (255, 255, 255), 743, 480, font)
            centeredMessage("is out!", (255, 255, 255), 743, 510, font)
            centeredMessage(")", (255, 255, 255), 785, 485, titleFont)

        try:
            pygame.draw.circle(screen, (255, 170, 0), ((selectedTile[0] * 60) + 65, (selectedTile[1] * 60) + 210), 20, 3)
        except:
            pass
        if activePlayer == computer: # let the computer have its turn
            pygame.display.flip() # update the display so that grid, name etc shows on the screen before time.wait
            pygame.time.wait(500) # pause for 500 ms
            computerStrike(targetPlayer)


    elif activeMenu == slotMachine:
        centeredMessage(f"£{gamble.betsize}", (255, 255, 255), 450, 605, font)
        centeredMessage(f"£{activePlayer.currency}", (255,255,255), 768, 190, font)
        centeredMessage(f"player: {activePlayer.name}", (255,255,255), 220, 190, font)

    elif activeMenu == winMenu:
        if winner == computer:
            centeredMessage(f"you LOST",(255,255,255),450,250,titleFont)
            centeredMessage("you lost to a clanker...... im so disappointed", (255,255,255),450,440,font)
        else:
            centeredMessage(f"{winner.name} wins!!! CONGARTS",(255,255,255),450,250,titleFont)
            centeredMessage("+£1000 for the winner", (0,255,0),450,360,titleFont)
            centeredMessage("good job winner", (255,255,255),450,440,font)

    # CONFIRM EXIT mini menu for gameplay
    if CEbuttons[0].active:
        for button in CEbuttons:
            button.draw()

    pygame.display.flip()
    clock.tick(10)
