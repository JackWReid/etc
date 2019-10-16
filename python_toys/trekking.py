#!/usr/bin/python

# coding: ascii
import os, sys, random

"""
DEFAULTS
"""

# 0 Plains
# 1 Hill
# 2 Monster
# 3 Chest
# 9 Door

defaultWorld = [
	[0,2,1,0,0,9],
	[0,1,0,1,3,1],
	[1,0,1,1,0,0],
	[2,3,0,3,0,0],
	[0,0,0,1,1,3],
	[0,1,1,3,2,3],
]

defaultLocation = {
	"y": 3,
	"x": 1
}

defaultHealth = 100
defaultHit = 10

defaultInventory = {
	"sword": False,
	"gun": False,
	"bike": False,
	"health": False,
	"key": False
}

"""
GAME
"""

gameWorld = defaultWorld
tileType = "null"


"""
USER
"""

userHealth = defaultHealth
userHit = defaultHit
userInventory = defaultInventory
userLocation = defaultLocation


"""
MONSTERS
"""

monsterBear = {
	"health": 60,
	"hit": 5
}

monsterLion = {
	"health": 40,
	"hit": 20
}


"""
INTERFACE
"""

def gameMenu():
	print "\n=========================================="
	print "   _            _    _    _               "
	print "  | |_ _ __ ___| | _| | _(_)_ __   __ _   "
	print "  | __| '__/ _ \ |/ / |/ / | '_ \ / _` |  "
	print "  | |_| | |  __/   <|   <| | | | | (_| |  "
	print "   \__|_|  \___|_|\_\_|\_\_|_| |_|\__, |  "
	print "                                  |___/   "
	print "==========================================\n"

	print "Welcome to Trekking. Pick up items to fend"
	print "off the monsters and get the hell out of  "
	print "here. Navigate by typing up, down, left or"
	print "right in the command.\n"

def gameInfo():
	os.system('clear')
	tileType = tileQuery()
	print "==================================="
	print("[Health: %s] [Strength: %s] %s" % (userHealth, userHit, tileType))
	inventoryInfo()
	print "==================================="

def inventoryInfo():
	if userInventory["sword"]:
		print "Sword [x]"
	else:
		print "Sword [ ]"

	if userInventory["gun"]:
		print "Gun   [x]"
	else:
		print "Gun   [ ]"

	if userInventory["bike"]:
		print "Bike  [x]"
	else:
		print "Bike  [ ]"

	if userInventory["health"]:
		print "Helth [x]"
	else:
		print "Helth [ ]"

	if userInventory["key"]:
		print "Key   [x]"
	else:
		print "Key   [ ]"

def userTurn():
	gameInfo()
	userMove()

"""
NAVIGATION
"""

def tileQuery():

	global tileType

	tileY = userLocation["y"]
	tileX = userLocation["x"]

	tileType = gameWorld[tileY][tileX]

	if tileType == 0:
		return "Plains"
	elif tileType == 1:
		return "Hills"
	elif tileType == 2:
		return "Monster"
	elif tileType == 3:
		return "Chest"
	elif tileType == 9:
		return "Door"
	else:
		print "Tile query failed."


def userMove():

	userDirection = raw_input("Move: ")
	
	userY = userLocation["y"]
	userX = userLocation["x"]

	if userInventory["bike"] == True:
		userSpeed = 2
	else:
		userSpeed = 1

	if userDirection == "up":
		if userY == 0:
			gameInfo()
			print "You hit the edge of the map."
			userCollide()
		else:
			userY = userY - userSpeed
			userLocation["y"] = userY
			userCollide()

	elif userDirection == "down":
		if userY == 5:
			gameInfo()
			print "You hit the edge of the map."
			userCollide()
		else:
			userY = userY + userSpeed
			userLocation["y"] = userY
			userCollide()

	elif userDirection == "left":
		if userX == 0:
			gameInfo()
			print "You hit the edge of the map."
			userCollide()
		else:
			userX = userX - userSpeed
			userLocation["x"] = userX
			userCollide()

	elif userDirection == "right":
		if userX == 5:
			gameInfo()
			print "You hit the edge of the map"
			userCollide()
		else:
			userX = userX + userSpeed
			userLocation["x"] = userX
			userCollide()

def userShuffle():

	global userLocation

	userY = random.randint(0,5)
	userX = random.randint(0,5)

	userLocation["y"] = userY
	userLocation["x"] = userX



"""
COLLISION
"""

def userCollide():
	if tileQuery() == "Plains":
		gamePlains()
	elif tileQuery() == "Hills":
		gameHills()
	elif tileQuery() == "Monster":
		gameMonster()
	elif tileQuery() == "Chest":
		gameChest()
	elif tileQuery() == "Door":
		gameDoor()
	else:
		print "User collide failed."


def gamePlains():
	raw_input("Easy plains. No action required.")
	userTurn()

def gameHills():
	raw_input("Straight hillage. No action required.")	
	userTurn()

def gameMonster():
	seedMonster = random.randint(0,1)
	spawnMonster = "null"

	if seedMonster == 0:
		spawnMonster == "bear"
	else:
		spawnMonster == "lion"

	raw_input("Ahhh it's a %s!" % (spawnMonster))
	userTurn()

def gameChest():
	chestItem = random.randint(0,4)

	print "You open up the chest to see what's inside."

	if chestItem == 0:
		userInventory["sword"] = True
		raw_input("You found a sword!")
		userTurn()
	elif chestItem == 1:
		userInventory["gun"] = True
		raw_input("You found a gun!")
		userTurn()
	elif chestItem == 2:
		userInventory["bike"] = True
		raw_input("You found a bike!")
		userTurn()
	elif chestItem == 3:
		userInventory["health"] = True
		raw_input("You found a health!")
		userTurn()
	elif chestItem == 4:
		userInventory["key"] = True
		raw_input("You found a key!")
		userTurn()
	else:
		raw_input("Chest item failed.")
		userTurn()

def gameFight():
	print ""

def gameDoor():
	print "You found a door! It has a lock."
	if userInventory["key"] == True:
		raw_input("You place a key in the lock.")
		gameWin()
	else:
		raw_input("The ground rumbles and you're thrown far away!")
		userShuffle()
		userTurn()


"""
MAIN
"""

gameMenu()
gameInfo()
userTurn()