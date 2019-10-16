#!/usr/bin/python

# coding: ascii
import os, sys, random

"""
GLOBALS
"""

# 0 = Flat
# 1 = Rock
# 2 = Monster
gameRidge = [0,0,0,0,0,0,0,0,0,0,0,0,0]

defaultLocation = len(gameRidge)/2
defaultHealth = 50
defaultEnergy = 50

userAim = 100
userHealth = 50
userEnergy = 50

userLocation = 0

"""
GENERATE WORLD
"""
def gameGenerate():
	for i in range(len(gameRidge)):
		gameRidge[i] = random.randint(0,2)

def gameDifficulty():
	global defaultHealth
	global defaultEnergy
	global userHealth
	global userEnergy
	global gameSettings

	gameSettings = raw_input("\nSET DIFFICULTY\neasy, medium, or hard? ")

	if gameSettings == "easy":
		defaultHealth = 100
		defaultEnergy = 100
		userHealth = 100
		userEnergy = 100
	elif gameSettings == "medium":
		defaultHealth = 100
		defaultEnergy = 100
		userHealth = 60
		userEnergy = 60
	elif gameSettings == "hard":
		defaultHealth = 100
		defaultEnergy = 100
		userHealth = 40
		userEnergy = 40
	else:
		gameDifficulty()


"""
PROMPTS
"""
# Plays at start of the game
def userWelcome():

	os.system('clear')

	print "*******************************"
	print "\n          WELCOME TO"
	print "______ ___________ _____  _____ "
	print "| ___ \_   _|  _  \  __ \|  ___|"
	print "| |_/ / | | | | | | |  \/| |__  "
	print "|    /  | | | | | | | __ |  __| "
	print "| |\ \ _| |_| |/ /| |_\ \| |___ "
	print "\_| \_|\___/|___/  \____/\____/ \n\n"
	print "*******************************\n\n"

	print "You're on a blustery ridge. You can't see"
	print "shit. You shuffle left or right. Try and"
	print "get off this dumb ass ridge."

	gameDifficulty()
	userPrompt()


def userInfo():
	os.system('clear')
	print "-------------------------------"
	print ("[Health: %i]      [Energy: %i]" % (userHealth, userEnergy))
	print "-------------------------------\n\n"

# Prompts user for direction
def userPrompt():
	global userLocation
	global userAim

	userInfo()
	userDirection = raw_input("What now? left or right? ")
	print "-------------------------\n\n"

	# Checks input and moves user
	if userDirection == "right":
		userAim = userLocation + 1
		userCollide()

	elif userDirection == "left":
		userAim = userLocation - 1
		userCollide()

	else:
		print "\nThat's not an option right now..."
		userPrompt()

# Checks for low health and energy (lose)
def userCheck():
	if userHealth < 1:
		userInfo()
		print "You succumb to your wounds and expire."
		endgameLose()
	elif userEnergy < 1:
		userInfo()
		print "You are exhausted and slump off the side of the ridge."
		endgameLose()
	else:
		userPrompt()



"""
ENCOUNTERS
"""
# Directs to encounters
def userCollide():
	global userLocation
	global userAim
	global gameRidge

	# Check if moving off array (win)
	if userAim > len(gameRidge) - 1:
		endgameWin()
	elif userAim == 0:
		endgameWin()
	# Otherwise, deal with what's there
	else:
		if gameRidge[userAim] == 0:
			encounterPlain()

		elif gameRidge[userAim] == 1:
			encounterRock()

		elif gameRidge[userAim] == 2:
			encounterMonster()



def encounterPlain():
	global userLocation
	global userAim
	global userEnergy
	userInfo()

	raw_input("You proceed easily over the flat area.\nEnter to continue...")
	userLocation = userAim
	userEnergy = userEnergy - 2
	userCheck()


def encounterRock():
	global userLocation
	global userAim
	global userEnergy
	userInfo()

	print "There's a big old rock in the way."
	userRockAction = raw_input("Well shit, what now?\nSmash or retreat? ")

	if userRockAction == "smash":
		userInfo()
		raw_input("You fucked up that rock's shit, son!\nEnter to continue... ")

		clearObstacle()
		userEnergy = userEnergy - 5
		userLocation = userAim
		userCheck()

	elif userRockAction == "retreat":
		userInfo()
		raw_input("Rocks scare you, you back it up.\nEnter to continue... ")

		userEnergy = userEnergy - 3
		userLocation = defaultLocation
		userCheck()

	else:
		userInfo()
		raw_input("You stare at the rock cluelessly for hours.\nEnter to continue... ")

		userEnergy = userEnergy - 2
		userCheck()


def encounterMonster():
	global userLocation
	global userAim
	global userEnergy
	userInfo()

	print "Holy crap, monster on the ridge!"
	userMonsterAction = raw_input("How do you deal with the monster...\nFight, chat, or retreat? ")
	
	if userMonsterAction == "fight":
		encounterFight()

	elif userMonsterAction == "chat":
		userInfo()
		raw_input("The monster lets you through after exhausting you with conversation.\nEnter to continue... ")
		userEnergy = userEnergy - 20
		clearObstacle()
		userLocation = userAim
		userCheck()

	elif userMonsterAction == "retreat":
		userInfo()
		raw_input("You run for the hills!\nEnter to continue... ")
		userEnergy = userEnergy - 7
		userLocation = defaultLocation
		userCheck()

	else:
		userInfo()
		raw_input("What? I didn't hear you. You're too dead.\nEnter to continue... ")
		endgameLose()

def encounterFight():
	global userHealth
	global userEnergy

	userDamage = random.randint(0,40)

	if userHealth - userDamage <= 0:
		userInfo()
		raw_input("You were flung from the ridge and into the abyss...\nEnter to continue... ")
		endgameLose()
	elif userDamage > 20:
		userInfo()
		raw_input("You defeated the beast, but at a cost. You are badly wounded and sapped of energy.\nEnter to continue... ")
		userHealth = userHealth - userDamage
		userEnergy = userEnergy - 10
		clearObstacle()
		userLocation = userAim
		userCheck()
	else:
		userInfo()
		raw_input("You got off lightly. The monster's dead but you feel knackered.\nEnter to continue... ")
		userHealth = userHealth - userDamage
		userEnergy = userEnergy - 10
		clearObstacle()
		userLocation = userAim
		userCheck()

def clearObstacle():
	gameRidge[userAim] = 0;


"""
END GAME SCENARIOS
"""
def endgameLose():
	print "GAME OVER."
	userRestart = raw_input("Restart? ")

	if userRestart == "yes":
		print "\nRestarting game...\n"
		userReset()
		userWelcome()
	else:
		print "\nQuitting...\n"

def endgameWin():
	print "You made it! Winner winner chicken dinner."
	userRestart = raw_input("Restart? ")

	if userRestart == "yes":
		print "\nRestarting game...\n"
		userReset()
		userWelcome()
	else:
		raw_input("\nQuitting...")
		os.system('clear')

def userReset():
	global userLocation
	global gameRidge
	global userHealth
	global userEnergy

	userHealth = defaultHealth
	userEnergy = defaultEnergy
	userLocation = defaultLocation
	gameGenerate()

	print "\n\n"

"""
MAIN
"""
userReset()
userWelcome()