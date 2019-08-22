# This filter creates staircases either at a corner or at a random point in the selection
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
	("Random Staircase Example", "label"),
	("Material", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	("Creator: Rodrigo Canaan", "label"),
	("Orientation", ("Linear", "Clockwise", "Counter-clockwise")),
	("Step Length", 1),
	("Vertical Buffer", 3),
	("Starting Direction", ("N","S","E","W")),
	("Starting Position", ("Random","Corner")),
	)

# MAIN SECTION #
# Every agent must have a "perform" function, which has three parameters
# 1: the level (aka the minecraft world). 2: the selected box from mcedit. 3: User defined inputs from mcedit
def perform(level, box, options):

	# Set up some variables based on the filter options
	if (options["Starting Position"] == "Random"):
		startx = random.randint(box.minx,box.maxx)
		startz = random.randint(box.minz,box.maxz)
	else:
		startx = box.minx
		startz = box.minz

	material = options["Material"].ID
	orientation = options["Orientation"]
	stepLength = options["Step Length"]
	verticalBuffer = options["Vertical Buffer"]
	direction = options["Starting Direction"]

	# Iterates along the y axis. For each heigh  y, creates a step at that heigh using setStep(), in the current direction and using the provided step length
	# The step in the current position starts from position (startx, y, startz), which is updated at each stept.
	for y in range (box.miny, box.maxy+1):
		# Create the current step
		(endx, endz) = setStep(level, startx, y, startz, material, direction, verticalBuffer, stepLength)

		# Update the starting position of the next step to the endpoint of the newly created step.
		startx = endx
		startz = endz

		# Get the direction of the next step acording to the current direction and the overall orientation of the staricases
		direction = getNextDirection(direction, orientation)


# Creates one step (a horizontal row of blocks)
# Parameters:
# 	level
# 	(startx, y, startz): starting position of the step
#	material: block material used in the step
#   direction: direction in which the step spreads
#	verticalBuffer: number of blocks above each inserted block that will be filled with air. This fills a dual purpose: removes any obstacles that could make the staircase impossible to climb, and allows you to build underground staricases
#	stepLength: length of the walkable  portion of the step. The total length is actually stepLength+1, since the last block of the step will have a new step above it (except for the last step of the staircase)
# Returns: (x,z) position of the last block in the step, so that a new step can be built on top of it.
def setStep(level, startx, y, startz, material, direction, verticalBuffer, stepLength):

	
	# Gets a unit-length vector in the direction of the step
	(deltax, deltaz) = getDeltaFromDirection(direction)

	# Populates the step using setBlockAndVerticalBuffer() for (stepLength+1) blocks
 	for offset in range(stepLength + 1):
		setBlockAndVerticalBuffer (level, material, startx + offset * deltax, y, startz + offset*deltaz, verticalBuffer)

	# Returns the (x, z) position of the last block
	return (startx + offset * deltax, startz + offset*deltaz )

def getDeltaFromDirection(direction):
	if direction == "N":
		return (0,-1)
	if direction == "S":
		return(0,1)
	if direction == "E":
		return(1,0)
	if direction == "W":
		return(-1,0)
 
# Fills a block in the (x,y,z) position with the given material.
# Fills with air a number of blocks equal to verticalBuffer
def setBlockAndVerticalBuffer (level, material, x, y, z, verticalBuffer):
	utilityFunctions.setBlock(level, (material,0), x, y, z)
	for h in range (1, verticalBuffer+1):
		utilityFunctions.setBlock(level,(0,0), x, y+h, z)

# Gets a next direction from the curent direction
# At the moment, the direction simply cycles in clockwise order
# TODO: Create an option in the input to enable other ways of selecting the next direction: clockwise, counter-clockwise, straight and random
def getNextDirection(direction, orientation):
	if orientation == "Linear":
		return direction

	elif orientation == "Clockwise":
		if direction == "N":
			return "E"
		if direction == "E":
			return "S"
		if direction == "S":
			return "W"
		if direction == "W":
			return "N"

	elif orientation == "Counter-clockwise":
		if direction == "N":
			return "W"
		if direction == "W":
			return "S"
		if direction == "S":
			return "E"
		if direction == "E":
			return "N"