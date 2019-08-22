# This filter creates a road using A* between start and end point
# This filter: rocanaan@gmail.com (mikecgreen.com)

import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions as utilityFunctions

#inputs are taken from the user. Here I've just showing labels, as well as letting the user define
# what the main creation material for the structures is
inputs = (
	("Connected Components", "label"),
	("Material", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	("Max Height", 255),
	("Min Height", 0),
	("Creator: Rodrigo Canaan", "label"),
	)


WATER = 9

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

	tileMap = getTileMap (level, box, options["Max Height"], options["Min Height"])

	colorMap = getColorMap(tileMap)
	print colorMap

	paintComponents(level,tileMap,colorMap,options["Material"].ID)

def paintComponents(level,tileMap,colorMap,material):
	for i in range(len(tileMap)):
		for j in range(len(tileMap[i])):
			if (tileMap[i][j].material!=WATER):
				tile = tileMap[i][j]
				print "painting {} {} with ".format(i,j,material)
				utilityFunctions.setBlock(level, (material+colorMap[i][j]-1, 0), tile.x, tile.y, tile.z)





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

def getColorMap(tileMap):

	currentColor = 1
	width = len(tileMap)
	depth = len(tileMap[0])
	colorMap = zeros((width,depth))
	for i in range(width):
		for j in range(depth):
			currentColor = fillColor(i,j,tileMap,colorMap,currentColor)

	return colorMap

def fillColor(i,j,tileMap,colorMap,currentColor):
	if i>=len(colorMap) or  j>=len(colorMap[0]) or i<0 or j<0: 
		return currentColor
	elif colorMap[i][j]!=0:
		return currentColor
	elif tileMap[i][j].material == WATER:
		colorMap[i][j] = -1
		return currentColor
	else:
		colorMap[i][j] = currentColor
		fillColor(i+1,j,tileMap,colorMap,currentColor)
		fillColor(i,j+1,tileMap,colorMap,currentColor)
		fillColor(i-1,j,tileMap,colorMap,currentColor)
		fillColor(i,j-1,tileMap,colorMap,currentColor)
		return currentColor+1

