# This filter creates a pillar at the highest point of the selection
# This filter: rocanaan@gmail.com 

import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions as utilityFunctions

inputs = (
	("CoG Tutorial Pillar", "label"), # A label with the name off our filter
	("Use Custom Material",True),
	("Material", alphaMaterials.Cobblestone),  # The  material to use
	("Height", 5), # The height of the pillar we're going to build
	("Creator: Rodrigo Canaan", "label"), # A label with the author of the filter
	)


# Class storing some properties of a tile in the game
class tile:
	def __init__(self, x, y, z, material):
		self.x = x
		self.y = y
		self.z = z
		self.material = material

# MAIN SECTION #
# Every agent must have a "perform" function, which has three parameters
# 1: the level (aka the minecraft world). 2: the selected box from mcedit. 3: User defined inputs from mcedit
def perform(level, box, options):

	#This creates an array of tile objects containing the (x,y,z) coordinates and material of the surface tile of every point in the selection
	tileMap = getTileMap (level, box, 255, 0)

	#This finds the tile with the highest y coordinate
	highestTile = getHighest(tileMap)

	#Creates a pillar on top of the highest tile
	makePillar(level,highestTile,options)

def getTileMap (level, box, maxHeight, minHeight):
	xmin = box.minx
	xmax = box.maxx
	zmin = box.minz
	zmax = box.maxz

	width = xmax-xmin+1
	depth = zmax-zmin+1

	tileMap = empty( (width,depth) ,dtype=object)

	for x in range(xmin,xmax+1):
		for z in range(zmin,zmax+1):
			for y in range(maxHeight, minHeight-1,-1):
				material = level.blockAt(x,y,z)
				if (material != 0):
					tileMap[x-xmin,z-zmin] = tile(x,y,z,material)
					print "Found block of type {} at position({},{},{})".format(material,x,y,z)
					break

	return tileMap

def getHighest(tileMap):
	ymax = -999
	highestTile = None
	for tile in tileMap.flatten():
		if (tile.y>=ymax):
			ymax = tile.y
			highestTile = tile
	return highestTile

def makePillar(level,highestTile,options):
	height = options["Height"]
	if (options["Use Custom Material"]==True):
		material = options["Material"].ID
	else:
		material = highestTile.material
	for step in range(height):
		utilityFunctions.setBlock(level, (material, 0), highestTile.x, highestTile.y+step+1, highestTile.z)


