from cmu_112_graphics import *
import random
import subprocess, threading, time
import pygame 

# image caching taken from PIL/Images zoom call
def getCachedPhotoImage(app, image):
#stores a cached version of the photoimage in the pil/pillow image
    if ('cachedPhotoImage' not in image.__dict__):
        image.cachedPhotoImage = ImageTk.PhotoImage(image)
    return image.cachedPhotoImage

def appStarted(app):
    #game mode 
    app.mode = 'splashScreenMode'

    #food list
    app.spawnedFood = []
    app.maxFoodPieces = 10

    #villain list
    app.spawnedVillains = []
    app.villainDelay = 0
    app.villainSpriteCounter = 0
    app.maxVillains = 0

    initImages(app)
    initVillainImages(app)
    initPowerUps(app)
    initCharacter(app)
    initsplash(app)
    newFoodPiece(app)

    app.rows = 25
    app.cols = 30
    app.margin = 5 # margin around grid

    #introduce a moving variable to indicate animation
    app.isMoving = False
    app.spriteCounter = 0
    app.direction = "Down"

    #game scores 
    app.scoreCounter = 0
    app.scoreTimer = 0

    #health bar
    app.hx = 50

    #level tracker
    app.levelTimer = 0
    app.level = 1

    #sound
    #CITATION : https://www.youtube.com/watch?v=FKZuGDQAO18
    pygame.mixer.init()
    app.sound = Sound('zelda1.mp3')

def appStopped(app):
    app.sound.stop()

def initCharacter(app):
    app.character = [(10, 5)]
    app.moveDirection = (0, +1) # (drow, dcol)
    app.gameOver = False

# getCellBounds from 112 notes : https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
def getCellBounds(app, row, col):
    # aka 'modelToView'
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    x0 = app.margin + gridWidth * col / app.cols
    x1 = app.margin + gridWidth * (col+1) / app.cols
    y0 = app.margin + gridHeight * row / app.rows
    y1 = app.margin + gridHeight * (row+1) / app.rows
    return (x0, y0, x1, y1)

#####################################
# Help Screen Mode
#####################################

def helpMode_redrawAll(app, canvas):
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.helpBackground))

    canvas.create_text(600, 100, text="How to Play :", font="Times 28 bold")

    canvas.create_text(600, 130, text="Goal :", font="Times 18 underline")
    canvas.create_text(600, 160, text="- Eat food to keep your health up", 
                        font="Times 14")
    canvas.create_text(600, 180, text="- Avoid villains", 
                        font="Times 14")
    canvas.create_text(600, 200, text="- Increase your score by eating food!", 
                        font="Times 14")
    
    canvas.create_text(600, 230, text="Power-Ups", 
                        font="Times 18 underline")
    canvas.create_image(600, 260, image=ImageTk.PhotoImage(app.speedImage))
    canvas.create_text(600, 290, text="- Speeds up your movement", 
                        font="Times 14")
    canvas.create_image(600, 320, image=ImageTk.PhotoImage(app.freezeImage))
    canvas.create_text(600, 350, text="- Freezes health bar", 
                        font="Times 14")
    canvas.create_image(600, 380, image=ImageTk.PhotoImage(app.stopImage))
    canvas.create_text(600, 410, text="- Stops villains from moving", 
                        font="Times 14")

    canvas.create_text(600, 450, text="Press any key to continue!", 
                        font="Times 26 bold")
    
def helpMode_keyPressed(app, canvas):
    app.mode = "gameMode"

#####################################
# Game over and score screen
#####################################

def endScreenMode_redrawAll(app, canvas):
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.endBackground))

    font = 'Times 26 bold'
    canvas.create_text(200, 200, text="YOU LOST!!", font=font)
    canvas.create_text(200, 300, 
                        text=f'Your score was : {app.scoreCounter}', font=font)
    canvas.create_text(200, 400,
                        text="Press R to play again!", font=font)
    
    highScore = readFile('score.txt')
    canvas.create_text(200, 350, 
                        text=f'Your high score is : {highScore}', fill = "Red",
                        font=font)

def endScreenMode_keyPressed(app, event):
    if (event.key == 'r'):
        app.mode = 'splashScreenMode'
    else:
        return

#####################################
# Splash Screen Mode
#####################################

def initsplash(app):
    splashBackground = 'splash screen.jpeg'
    # CITATION : https://wallpaperaccess.com/pichu

    app.splashScreen = app.loadImage(splashBackground)
    app.splashScreen = app.scaleImage(app.splashScreen, 0.67)

    helpBackground = 'pichu background.jpeg'
    # CITATION : https://wallpaperaccess.com/pichu
    app.helpBackground = app.loadImage(helpBackground)
    app.helpBackground = app.scaleImage(app.helpBackground, 0.65)

    endBackground = 'end screen.jpeg'
    # CITATION : https://wallpapercave.com/pichu-wallpaper
    app.endBackground = app.loadImage(endBackground)
    app.endBackground = app.scaleImage(app.endBackground, 0.55)

def splashScreenMode_redrawAll(app, canvas):
    #background image for splash screen
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.splashScreen))

    font = "Times 50 bold"
    canvas.create_text(app.width//2, app.height//2 - 200, 
                        text="Hungry Pichu", font=font)
    canvas.create_text(app.width//2, app.height//2 - 100, 
                        text="Click any key to begin", font="Times 26")

def splashScreenMode_keyPressed(app, event):
    # #reset everything
    appStarted(app)
    #new villains 
    newVillain(app)
    #change game mode 
    app.mode = 'gameMode'
    #start sound
    app.sound.start(loops = -1)

#####################################
# Game mode
#####################################

def gameMode_keyPressed(app, event):

    if app.gameOver:
        return
    
    elif (event.key == "h"):
        app.mode = 'helpMode'

    elif (event.key == 'Up'): 
        app.direction = event.key   
        if app.speedMode == True:
            app.moveDirection = (-2, 0)
        else:
            app.moveDirection = (-1, 0)
        moveCharacter(app)

    elif (event.key == 'Down'): 
        app.direction = event.key 
        if app.speedMode == True:
            app.moveDirection = (+2, 0)
        else:
            app.moveDirection = (+1, 0)
        moveCharacter(app)

    elif (event.key == 'Left'):  
        app.direction = event.key 
        if app.speedMode == True:
            app.moveDirection = (0, -2)
        else:
            app.moveDirection = (0, -1)
        moveCharacter(app)

    elif (event.key == 'Right'): 
        app.direction = event.key 
        if app.speedMode == True:
            app.moveDirection = (0, +2)
        else:
            app.moveDirection = (0, +1)
        moveCharacter(app)
    
    elif (event.key == 's'):
        if app.sound.isPlaying():
            app.sound.stop()
        else:
            app.sound.start()
    
def gameMode_timerFired(app):

    if app.gameOver:
        return

    #spawn food
    newFoodPiece(app)

    #spawn villain
    newVillain(app)
    #make villain move
    app.villainDelay += 1
    #to slow villain down 
    if (app.stopMode == False):
        if (app.villainDelay % 2 == 0):
            makeVillainMove(app)

    #sprite movement
    if app.isMoving:
        app.spritecounter = (app.spriteCounter + 1) % 6
    else:
        app.spriteCounter = 0
    
    #health bar 
    if (app.freezeMode == False):
        if (app.hx < (app.width - 50)):
            app.hx += 1
    #if health bar gone then you lose   
    if (app.hx >= (app.width - 200)):
        app.gameOver = True
        app.mode = 'endScreenMode'

        #keep track of best score
        highScore = readFile('score.txt')
        if highScore == '':
            highScore = app.scoreCounter
            writeFile('score.txt', repr(highScore))
        else:
            if app.scoreCounter > int(highScore):
                highScore = app.scoreCounter
                writeFile('score.txt', repr(highScore))
    
    # spawn power up foods 
    newSpeedFood(app)
    newFreezeFood(app)
    newStopFood(app)

    #speed food timer
    if app.speedMode == True:
        app.speedModeTimer += 1
        if app.speedModeTimer == 50:
            app.speedMode = False
            app.speedModeTimer = 0
    # freeze health bar timer
    if app.freezeMode == True:
        app.freezeModeTimer += 1
        if app.freezeModeTimer == 25:
            app.freezeMode = False
            app.freezeModeTimer = 0

    # stop food poewr up timer
    if app.stopMode == True:
        app.stopModeTimer += 1
        if app.stopModeTimer == 50:
            app.stopMode = False
            app.stopModeTimer = 0
    
    #level tracker
    app.levelTimer += 1
    if (app.levelTimer % 100 == 0):
        #keep track of level
        if app.level <= 3:
            app.level += 1
        #keep track of number of villains per level 
        if app.maxVillains < 2:
            app.maxVillains += 1
        #keep track of food spawned during each level
        if app.maxFoodPieces > 2:
            app.maxFoodPieces -= 2

#read and write file to keep track of high score
#CITATION : https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, 'rt') as f:
        return f.read()

def writeFile(path, contents):
    with open(path, 'wt') as f:
        f.write(contents)

def collision(newRow, newCol):

    #make sure character can't go beyond borders
    if ((newRow < 3) or (newRow >= 23) or
        (newCol < 1) or (newCol >= 29)):
        if (23 <= newRow <= 24) and (9 <= newCol <= 13):
            return False
        return True
    #cant climb cliff 1
    if (9 <= newRow <= 12) and (1 <= newCol <= 4):
        return True
    
    if (9 <= newRow <= 12) and (8 <= newCol <= 11):
        return True
    #dont run into tree
    if (9 <= newRow <= 14) and (11 <= newCol <= 13):
        return True
    #dont run into water
    if (0 <= newRow <= 25) and (14 <= newCol <= 16):
        #go across bridge
        if (7 <= newRow <= 8):
            return False
        return True   
    #trees
    if (0 <= newRow <= 4) and (0 <= newCol <= 6):
        return True
    
    if (0 <= newRow <= 4) and (9 <= newCol <= 11):
        return True
    
    if (0 <= newRow <= 5) and (16 <= newCol <= 20):
        return True
    #dont go off cliff 2
    if (9 <= newRow <= 13) and (17 <= newCol <= 18):
        return True
    
    if (13 <= newRow <= 16) and (18 <= newCol <= 20):
        return True
    
    if (13 <= newRow <= 16) and (23 <= newCol <= 26):
        return True
    
    if (8 <= newRow <= 9) and (23 <= newCol <= 25):
        return True
    #treasure box
    if (6 <= newRow <= 7) and (25 <= newCol <= 26):
        return True
    
    if (0 <= newRow <= 5) and (25 <= newCol <= 30):
        return True

    if (0 <= newRow <= 4) and (24 <= newCol <= 25):
        return True
    #stones
    if (19 <= newRow <= 20) and (21 <= newCol <= 22):
        return True

def moveCharacter(app):
    app.spriteCounter = (app.spriteCounter + 1) % 6

    (drow, dcol) = app.moveDirection
    (headRow, headCol) = app.character[0]
    (newRow, newCol) = (headRow+drow, headCol+dcol)

    if collision(newRow, newCol) == True:
        return

    app.character.insert(0, (newRow, newCol))

    app.character.pop()
    #if character and food collide
    for food in app.spawnedFood:

        if ((food.row - 1 <= newRow <= food.row + 1) and 
            (food.col - 1 <= newCol <= food.col + 1)):
            #remove food
            app.spawnedFood.remove(food)
            #spawn new food
            newFoodPiece(app)
            #health goes up 
            if (app.hx < 50) == False:
                app.hx -= 10
            #score goes up
            app.scoreCounter += 1
    
    for powerUp in app.spawnedPowerUps:
        if ((powerUp.row - 1 <= newRow <= powerUp.row + 1) and 
            (powerUp.col - 1 <= newCol <= powerUp.col + 1)):

            #speed power up
            if (isinstance(powerUp, speedFood)):
                app.speedMode = True
            #freeze health bar power up
            if (isinstance(powerUp, freezeFood)):
                app.freezeMode = True
            # stop villain power up
            if (isinstance(powerUp, stopFood)):
                app.stopMode = True
            #remove food
            app.spawnedPowerUps.remove(powerUp)
        
def makeVillainMove(app):
    app.villainSpriteCounter = (app.villainSpriteCounter + 1) % 4

    for (row, col) in app.character:
        targetRow, targetCol = row, col

    for villain in app.spawnedVillains:
        villain.moveVillain(targetRow, targetCol)

    #if villain and player collide, game ends
    playerCoords = app.character[0]
    playerRow = playerCoords[0]
    playerCol = playerCoords[1]

    for villain in app.spawnedVillains:
            
        if ((villain.row-0.5 <= playerRow <= villain.row+0.5) and 
            (villain.col-0.5 <= playerCol <= villain.col+0.5)):
            app.gameOver = True
            app.mode = 'endScreenMode'
            app.sound.stop()

            #keep track of best score
            highScore = readFile('score.txt')
            if highScore == '':
                highScore = app.scoreCounter
                writeFile('score.txt', repr(highScore))
            else:
                if app.scoreCounter > int(highScore):
                    highScore = app.scoreCounter
                    writeFile('score.txt', repr(highScore))

def initImages(app):

    #sprite sheet iteration and background code modified from PIL/images zoom call
    currentBackground = 'game background.png'
    #CITATION : image link : https://www.pinterest.es/pin/392939136223271193/

    #scale everything to fit window   
    app.backgroundImage = app.loadImage(currentBackground)
    app.backgroundImage = app.scaleImage(app.backgroundImage, 1)

    #initialize background width and size, do not allow player to leave
    app.backgroundWidth, app.backgroundHeight = app.backgroundImage.size


    characterSpriteSheet = 'pokemon2.png'
    #CITATION : image link : https://rpgdreams.forumotion.com/t246p15-pokemon-series-overworld-sprites
    app.spriteSheet = app.loadImage(characterSpriteSheet)
    app.spriteSheet = app.scaleImage(app.spriteSheet, 2.5)
    app.spriteHeight, app.spriteWidth = app.spriteSheet.size

    #movements in sprite list with dict
    app.sprites = dict()
    imageWidth = app.spriteSheet.width
    imageHeight = app.spriteSheet.height

    for direction in ("Down0", "Left1", "Right2", "Up3"):

        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * (imageHeight / 4)
        botRighty = (index + 1) * (imageHeight / 4)
        tempSprites = []

        for j in range(4):

            topLeftx = j * (imageWidth / 6)
            botRightx = (j + 1) * (imageWidth / 6)

            sprite = app.spriteSheet.crop((topLeftx, topLefty, 
                                            botRightx, botRighty))
            tempSprites.append(sprite)

        app.sprites[newDir] = tempSprites
    
    # food images
    foodSheet = 'food sprite5.png'
    #CITATION : image link : https://www.vhv.rs/viewpic/hwmRiTh_junk-food-sprite-png-transparent-png/

    app.foodSheet = app.loadImage(foodSheet)
    app.foodSheet = app.scaleImage(app.foodSheet, 0.25)

    app.foodPieces = []
    # add food from sheet into list
    for i in range(3):
        topLeftY = i * 43
        bottomRightY = topLeftY + 43

        for j in range(3):
            topLeftX = j * 45
            bottomRightX = topLeftX + 45

            food = app.foodSheet.crop((topLeftX, topLeftY, 
                                    bottomRightX, bottomRightY))

            app.foodPieces.append(food)

def initPowerUps(app):
    #-------------------------
    # speed power up
    #-------------------------
    speedImage = 'aguav berry.png'
    #CITATION : https://bulbapedia.bulbagarden.net/wiki/Aguav_Berry
    app.speedImage = app.loadImage(speedImage)
    app.speedImage = app.scaleImage(app.speedImage, 0.15)

    app.spawnedPowerUps = []
    app.speedMode = False
    app.speedModeTimer = 0

    #--------------------------
    # freeze health bar power up
    #--------------------------
    freezeImage = 'mago berry.png'
    #CITATION : https://pokemon.fandom.com/wiki/Mago_Berry
    app.freezeImage = app.loadImage(freezeImage)
    app.freezeImage = app.scaleImage(app.freezeImage, 0.15)

    app.freezeMode = False
    app.freezeModeTimer = 0

    #---------------------------
    # stop villain movement power up
    #---------------------------
    stopImage = 'olive berry.png'
    #CITATION : https://pokemon.fandom.com/wiki/Category:Berries_that_make_Olive_Pok%C3%A9blocks
    app.stopImage = app.loadImage(stopImage)
    app.stopImage = app.scaleImage(app.stopImage, 0.1)

    app.stopMode = False
    app.stopModeTimer = 0

def initVillainImages(app): 

    #Villain images 
    villain0 = 'villain1 .png'
    villain1 = 'villain 2.png'
    #CITATION : image link : https://www.deviantart.com/purplezaffre/gallery

    app.villain0Sheet = app.loadImage(villain0)
    app.villain1Sheet = app.loadImage(villain1)

    app.villain0Sheet = app.scaleImage(app.villain0Sheet, 1)
    app.villain1Sheet = app.scaleImage(app.villain1Sheet, 1)

    #creating image dictionary for villain 0 (Guzma)
    app.villain0 = dict()
    imageWidth, imageHeight = app.villain0Sheet.width, app.villain0Sheet.height

    for direction in ("Down0", "Left1", "Right2", "Up3"):

        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * (imageHeight / 4)
        botRighty = (index + 1) * (imageHeight / 4)
        tempSprites = []

        for j in range(4):

            topLeftx = j * (imageWidth / 4)
            botRightx = (j + 1) * (imageWidth / 4)

            sprite = app.villain0Sheet.crop((topLeftx, topLefty, 
                                            botRightx, botRighty))
            tempSprites.append(sprite)

        app.villain0[newDir] = tempSprites
    
    #creating image dictionary for villain 1 (ghetsis)
    app.villain1 = dict()
    imageWidth, imageHeight = app.villain1Sheet.width, app.villain1Sheet.height

    for direction in ("Down0", "Left1", "Right2", "Up3"):

        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * (imageHeight / 4)
        botRighty = (index + 1) * (imageHeight / 4)
        tempSprites = []

        for j in range(4):

            topLeftx = j * (imageWidth / 4)
            botRightx = (j + 1) * (imageWidth / 4)

            sprite = app.villain1Sheet.crop((topLeftx, topLefty, 
                                            botRightx, botRighty))
            tempSprites.append(sprite)

        app.villain1[newDir] = tempSprites

def newFoodPiece(app):

    #dont spawn food if theres too much on map already
    if len(app.spawnedFood) > app.maxFoodPieces:
        return 
    #randomizing type of food and spawn location 
    randomIndex = random.randint(0, len(app.foodPieces) - 1)

    randomRow = random.randint(0, 25)
    randomCol = random.randint(0, 30)

    #assign food piece to random food from list
    image = app.foodPieces[randomIndex]

    if collision(randomRow, randomCol):
        return

    #create new food object
    newFood = Food(randomRow, randomCol, image)

    #add object to list
    app.spawnedFood.append(newFood)

def newSpeedFood(app):
    if len(app.spawnedPowerUps) == 3:
        return
    #randomize food location
    randomRow = random.randint(0, 25)
    randomCol = random.randint(0, 30)

    if collision(randomRow, randomCol):
        return
    #make new food object
    newSpeedFood = speedFood(randomRow, randomCol, app.speedImage)
    #add to spawned list
    app.spawnedPowerUps.append(newSpeedFood)

def newFreezeFood(app):
    if len(app.spawnedPowerUps) == 3:
        return
    #randomize food location
    randomRow = random.randint(0, 25)
    randomCol = random.randint(0, 30)

    if collision(randomRow, randomCol):
        return
    #make new food object
    newFreezeFood = freezeFood(randomRow, randomCol, app.freezeImage)
    #add to spawned list
    app.spawnedPowerUps.append(newFreezeFood)

def newStopFood(app):
    if len(app.spawnedPowerUps) == 3:
        return
    #randomize food location
    randomRow = random.randint(0, 25)
    randomCol = random.randint(0, 30)

    if collision(randomRow, randomCol):
        return
    #make new food object
    newStopFood = stopFood(randomRow, randomCol, app.stopImage)
    #add to spawned list
    app.spawnedPowerUps.append(newStopFood)

def newVillain(app):

    if len(app.spawnedVillains) >= app.maxVillains:
        return
    
    if app.level == 3:
        guzma = Guzma(7, 20, app.villain0)
        app.spawnedVillains.append(guzma)

    if app.level == 2:
        ghetsis = Ghetsis(7, 14, app.villain1)
        app.spawnedVillains.append(ghetsis)

# CITATION : https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#playingSoundsWithPygame
class Sound(object):
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())
    
    def start(self, loops = 1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)
    
    def stop(self):
        pygame.mixer.music.stop()

class Food(object):

    def __init__(self, row, col, image):
        self.row = row
        self.col = col
        self.image = image

class speedFood(Food):
    def __init__(self, row, col, image):
        super().__init__(row, col, image)
    
    def drawFood(self, app, canvas):
        row = self.row
        col = self.col

        (x0, y0, x1, y1) = getCellBounds(app, row, col)

        speedImage = self.image
        canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                        image=ImageTk.PhotoImage(speedImage))

class freezeFood(Food):
    def __init__(self, row, col, image):
        super().__init__(row, col, image)
    
    def drawFood(self, app, canvas):
        row = self.row
        col = self.col

        (x0, y0, x1, y1) = getCellBounds(app, row, col)

        freezeImage = self.image
        canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                        image=ImageTk.PhotoImage(freezeImage))

class stopFood(Food):
    def __init__(self, row, col, image):
        super().__init__(row, col, image)
    
    def drawFood(self, app, canvas):
        row = self.row
        col = self.col

        (x0, y0, x1, y1) = getCellBounds(app, row, col)

        stopImage = self.image
        canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                        image=ImageTk.PhotoImage(stopImage))

class Villain(object):

    def __init__(self, row, col, imageDict):
        self.row = row
        self.col = col
        self.imageDict = imageDict

        #variables modified from : https://github.com/asaxena2019/pacman/blob/master/ghost.py
        self.currDirection = "Down"
        self.legalDirections = ["Up", "Down", "Left", "Right"]

        self.speed = 1

        self.dcol = 0
        self.drow = 1*self.speed

    def coordSetter(self):
        if self.currDirection == "Up":
            self.dcol = 0
            self.drow = -1*self.speed

        if self.currDirection == "Down":
            self.dcol = 0
            self.drow = 1*self.speed

        if self.currDirection == "Left":
            self.dcol = -1*self.speed
            self.drow = 0

        if self.currDirection == "Right":
            self.dcol = 1*self.speed
            self.drow = 0

    def moveVillain(self):
        #called in individual villain classes
        pass

    def drawVillain(self, app, canvas):
        row = self.row
        col = self.col

        (x0, y0, x1, y1) = getCellBounds(app, row, col)

        villainImage = self.imageDict[self.currDirection][app.spriteCounter]
        canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                        image=ImageTk.PhotoImage(villainImage))

#Node class written from : https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
#Node class for a* pathfinding
class Node():
    
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position
        
        self.gScore = 0
        self.hScore = 0
        self.fScore = 0
    
    def __eq__(self, other):
        return self.position == other.position 

#pseudocode used from : https://en.wikipedia.org/wiki/A*_search_algorithm
def astar(start, end):
    #if there is a collision, return
    if (start[0] == end[0] and start[1] == end[1]):
        return None

    #initialize open and closed list
    openList = []
    closedList = []

    #initialize nodeStart
    nodeStart = Node(None, start)
    #initialize nodeGoal
    nodeGoal = Node(None, end)

    # add nodeStart to open list 
    openList.append(nodeStart)

    #while open list is not empty 
    while (len(openList) > 0):
        # find node in open list with lowest f score 
        smallest = 1000
        currNode = None
        for openChild in openList:
            if openChild.fScore < smallest:
                currNode = openChild
                smallest = openChild.fScore

        #found the goal
        if currNode == nodeGoal:
            #backtrack to get path
            path = []
            selectedNode = currNode

            while selectedNode is not None:
                path.append(selectedNode.position)
                selectedNode = selectedNode.parent

            return path[::-1]

        else:    
            #remove current node from open list
            openList.remove(currNode)
            #put current node in closed list
            closedList.append(currNode)
            #generate neighbors
            nodeNeighbors = []
            currNodePosition = currNode.position
            legalMoves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for move in legalMoves:
                moveRow = move[0]
                moveCol = move[1]
                newPosition = (currNodePosition[0] + moveRow, 
                                currNodePosition[1] + moveCol)
                if collision(newPosition[0], newPosition[1]):
                    continue
                else:
                    nodeNeighbors.append(Node(currNode, newPosition))
            
            #for each neighbor of current node
            for neighbor in nodeNeighbors:
                #find f, g, h values
                # 1 is the distance (weight) between the current node and neighbor
                neighbor.gScore = currNode.gScore + 1
                #use distance formula for heuristic (h)
                neighbor.hScore = (((nodeGoal.position[0] - neighbor.position[0])**2) +
                            ((nodeGoal.position[1] - neighbor.position[1])**2))
                neighbor.fScore = neighbor.gScore + neighbor.hScore 

                if neighbor not in openList:
                    openList.append(neighbor)

class Guzma(Villain):
    def __init__(self, row, col, imageDict):
        super().__init__(row, col, imageDict)

    def moveVillain(self, targetRow, targetCol):

        #make path 
        start = (self.row, self.col)
        end = (targetRow, targetCol)
        path = astar(start, end)

        if path == None:
            return

        #move villain along path 
        startPath = path[0]
        target = path[1]

        if target[0] - startPath[0] == 0:
            if startPath[1] <= target[1] or target[1] == 30:
                self.currDirection = "Right"
            elif startPath[1] > target[1] or target[1] == 0:
                self.currDirection = "Left"
        else:
            if startPath[0] <= target[0] or target[0] == 25:
                self.currDirection = "Down"
            elif startPath[0] > target[0] or target[0] == 0:
                self.currDirection = "Up"
        
        self.coordSetter()

        self.row += self.drow
        self.col += self.dcol

class Ghetsis(Villain):
    def __init__(self, row, col, imageDict):
        super().__init__(row, col, imageDict)

    #dumb algorithm to move villain
    def moveVillain(self, targetRow, targetCol):
        startRow = self.row
        startCol = self.col

        endRow = targetRow
        endCol = targetCol 

        if startRow > endRow:
            if startCol > endCol:
                if startRow - endRow > startCol - endCol:
                    self.currDirection = "Up"
                else: 
                    self.currDirection = "Left"
            else:
                if startRow - endRow > endCol - startCol:
                    self.currDirection = "Up"
                else:
                    self.currDirection = "Right"
        else:
            if startCol > endCol:
                if endRow - startRow > startCol - endCol:
                    self.currDirection = "Down"
                else:
                    self.currDirection = "Left"
            else:
                if endRow - startRow > endCol - startCol:
                    self.currDirection = "Down"
                else:
                    self.currDirection = "Right"
        
        self.coordSetter()

        if (collision(self.row + self.drow, self.col + self.dcol)):
            return

        self.row += self.drow
        self.col += self.dcol

def drawFood(app, canvas): 
    if app.spawnedFood == []:
        return 

    for food in app.spawnedFood:
        (x0, y0, x1, y1) = getCellBounds(app, food.row, food.col)
        canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                        image=ImageTk.PhotoImage(food.image))

def drawPowerUps(app, canvas):
    for food in app.spawnedPowerUps:
        food.drawFood(app, canvas)

def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill='white')

def drawHealth(app, canvas):
    #draw green health bar
    canvas.create_rectangle(50, 10, app.width - 200, 30, fill="palegreen")
    #draw red health bar
    if (app.hx < 50):
        return 

    canvas.create_rectangle(50, 10, app.hx, 30, fill="lightcoral")

def drawScore(app, canvas):
    scoreDisplay = "Score : " + str(int(app.scoreCounter))
    canvas.create_text(app.width - 50, 20, text = scoreDisplay, 
                        fill = "Black", font = "Arial 16 bold")

def drawCharacter(app, canvas):
    for (row, col) in app.character:
        (x0, y0, x1, y1) = getCellBounds(app, row, col)

    spriteImage = app.sprites[app.direction][app.spriteCounter]
    canvas.create_image((x1+x0)/2, (y1+y0)/2, 
                            image=getCachedPhotoImage(app, spriteImage))

def drawLevel(app, canvas):
    levelDisplay = "Level : " + str(int(app.level))
    canvas.create_text(app.width - 50, 35, text = levelDisplay, 
                        fill = "Black", font = "Arial 16 bold")

def drawPowerUpDisplay(app, canvas):
    if app.speedMode == True:
        speedDisplay = "SPEED ACTIVATED!!"
        canvas.create_text(100, 40, text = speedDisplay, 
                        fill = "Orange", font = "Arial 16 bold")
    if app.freezeMode == True:
        freezeDisplay = "FREEZE ACTIVATED!!"
        canvas.create_text(100, 55, text = freezeDisplay, 
                        fill = "Blue", font = "Arial 16 bold")
    if app.stopMode == True:
        stopDisplay = "STOP ACTIVATED!!"
        canvas.create_text(100, 70, text = stopDisplay, 
                        fill = "Red", font = "Arial 16 bold")

def drawBackground(app, canvas):
    imageWidth, imageHeight = app.backgroundImage.size
    backgroundImage = getCachedPhotoImage(app, app.backgroundImage)
    canvas.create_image(0, 0, image=backgroundImage, anchor="nw")

def gameMode_redrawAll(app, canvas):

    #draw background
    drawBackground(app, canvas)

    #draw character
    drawCharacter(app, canvas)

    #draw villain 
    for villain in app.spawnedVillains:
        villain.drawVillain(app, canvas)

    #draw health bar and score and level
    drawHealth(app, canvas)
    drawScore(app, canvas)
    drawLevel(app, canvas)

    #draw food
    drawFood(app, canvas)
    #draw power up food
    drawPowerUps(app, canvas)
    drawPowerUpDisplay(app, canvas)

runApp(width=800, height=600)