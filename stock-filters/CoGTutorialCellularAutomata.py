# This filter procedurally generates 4 structures within the selection box within defined limits
# This filter: mcgreentn@gmail.com (mikecgreen.com)

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
	("Cellular Automata SG Example", "label"),
	("Material", alphaMaterials.Cobblestone), # the material we want to use to build the mass of the structures
	("Creator: Michael Green", "label"),
	)


# MAIN SECTION #
# Every agent must have a "perform" function, which has three parameters
# 1: the level (aka the minecraft world). 2: the selected box from mcedit. 3: User defined inputs from mcedit
def perform(level, box, options):
	yards = binaryPartition(box)
	# for each quadrant
	for yard in yards:
		buildFence(level, yard)
		buildStructure(level, yard, options)

#splits the given box into 4 unequal areas
def binaryPartition(box):
	partitions = []
	# create a queue which holds the next areas to be partitioned
	queue = []
	queue.append(box)
	# for as long as the queue still has boxes to partition...
	count = 0
	while len(queue) > 0:
		count += 1
		splitMe = queue.pop(0)
		(width, height, depth) = utilityFunctions.getBoxSize(splitMe)
		# print "Current partition width,depth",width,depth 
		centre = 0
		# this bool lets me know which dimension I will be splitting on. It matters when we create the new outer bound size
		isWidth = False
		# find the larger dimension and divide in half
		# if the larger dimension is < 10, then block this from being partitioned
		minSize = 12
		if width > depth:
			# roll a random die, 1% change we stop anyways
			chance = random.randint(100)

			if depth < minSize or chance == 1:
				partitions.append(splitMe)
				continue

			isWidth = True
			centre = width / 2
		else:
			chance = random.randint(10)
			if width < minSize or chance == 1:
				partitions.append(splitMe)
				continue				
			centre = depth / 2

		# a random modifier for binary splitting which is somewhere between 0 and 1/16 the total box side length
		randomPartition = random.randint(0, (centre / 8) + 1)

		# creating the new bound
		newBound = centre + randomPartition

		#creating the outer edge bounds
		outsideNewBounds = 0
		if isWidth:
			outsideNewBound = width - newBound - 1
		else:
			outsideNewBound = depth - newBound - 1

		# creating the bounding boxes
		# NOTE: BoundingBoxes are objects contained within pymclevel and can be instantiated as follows
		# BoundingBox((x,y,z), (sizex, sizey, sizez))
		# in this instance, you specifiy which corner to start, and then the size of the box dimensions
		# this is an if statement to separate out binary partitions by dimension (x and z)
		if isWidth:
			queue.append(BoundingBox((splitMe.minx, splitMe.miny, splitMe.minz), (newBound-1, 256, depth)))
			queue.append(BoundingBox((splitMe.minx + newBound + 1, splitMe.miny, splitMe.minz), (outsideNewBound - 1, 256, depth)))
		else:
			queue.append(BoundingBox((splitMe.minx, splitMe.miny, splitMe.minz), (width, 256, newBound - 1)))
			queue.append(BoundingBox((splitMe.minx, splitMe.miny, splitMe.minz + newBound + 1), (width, 256, outsideNewBound - 1)))
	return partitions

# builds a wooden fence around the perimeter of this box, like this photo
#			  Top - zmax
#       ----------------
#       |              |
#       |              |
#       |              |
# Left  |              | Right
# xmin  |              | xmax
#       |              |
#       |              |
#       ----------------
#			Bottom - zmin
def buildFence(level, box):

	# side by side, go row/column by row/column, and move down the pillar in the y axis starting from the top
	# look for the first non-air tile (id != 0). The tile above this will be a fence tile

	# add top fence blocks
	for x in range(box.minx, box.maxx):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(x, y, box.maxz)
				if tempBlock != 0:
					newValue = 0
					utilityFunctions.setBlock(level, (85, newValue), x, y+1, box.maxz)
					break;
	# add bottom fence blocks (don't double count corner)
	for x in range(box.minx, box.maxx):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(x, y, box.minz)
				if tempBlock != 0:
					newValue = 0
					utilityFunctions.setBlock(level, (85, newValue), x, y+1, box.minz)
					break;
	# add left fence blocks (don't double count corner)
	for z in range(box.minz+1, box.maxz):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(box.minx, y, z)
				if tempBlock != 0:
					newValue = 0
					utilityFunctions.setBlock(level, (85, newValue), box.minx, y+1, z)
					break;
	# add right fence blocks
	for z in range(box.minz, box.maxz+1):
		for y in xrange(box.maxy, box.miny, -1):
				# get this block
				tempBlock = level.blockAt(box.maxx, y, z)
				if tempBlock != 0:
					newValue = 0
					utilityFunctions.setBlock(level, (85, newValue), box.maxx, y+1, z)
					break;

# builds a structure (the material of which is specified by user in inputs) within the given box
# 4 steps:
# 1. decide the floor plan, map out the foundations of the building, build floor
# 2. create corner pillars
# 3. between each pair of pillars, use Cellular Automata to build a wall
# 4. create celing at the ceiling level
def buildStructure(level, box, options):
	floor = makeFloorPlan(level, box)
	buildingHeightInfo = createPillars(level, floor, options)
	generateWalls(level, floor, buildingHeightInfo, options)
	generateCeiling(level, floor, buildingHeightInfo, options)

def makeFloorPlan(level, box):
	# we have to first figure out where in the box this is going to be
	# find the box dimensions
	(width, height, depth) = utilityFunctions.getBoxSize(box)

	# get sixths
	fractionWidth = width / 6
	fractionDepth = depth / 6
	# create the box boundaries
	randFracx = random.randint(0, fractionWidth+1)
	randFracz = random.randint(0, fractionDepth+1)
	xstart = box.minx +  randFracx + 2
	zstart = box.minz + randFracz + 2

	xsize = width * 0.6 - randFracx
	zsize = depth * 0.6 - randFracz

	floorplan = BoundingBox((xstart, box.miny, zstart), (xsize, box.maxy, zsize))
	return floorplan

# we need to create the corners for the walls.
#Every building needs corners for stability...unless you are inventive... :)
def createPillars(level, floor, options):
	cornerBlockStarts = []
	ycoords = []
	# similarly to fences, we need to countdown on each of the four corners and find the block where the ground starts, then start building pillars above that height
	midpointFloorHeight = 0
	for y in xrange(floor.maxy, floor.miny-1, -1):
		# get this block
		tempBlock = level.blockAt(floor.minx, y, floor.minz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.minx, y+1, floor.minz))
			break;
	for y in xrange(floor.maxy, floor.miny-1, -1):
		# get this block
		tempBlock = level.blockAt(floor.minx, y, floor.maxz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.minx, y+1, floor.maxz))
			break;
	for y in xrange(floor.maxy, floor.miny-1, -1):
		# get this block
		tempBlock = level.blockAt(floor.maxx, y, floor.minz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.maxx, y+1, floor.minz))
			break;
	for y in xrange(floor.maxy, floor.miny-1, -1):
		# get this block
		tempBlock = level.blockAt(floor.maxx, y, floor.maxz)
		if tempBlock != 0:
			cornerBlockStarts.append((floor.maxx, y+1, floor.maxz))
			break;

	# now we have all four corners. for each, pick a random y value between 5 and 45, and build up using stone
	ystartCoordMax = -10000
	for cornerstone in cornerBlockStarts:
		midpointFloorHeight += cornerstone[1]
		if(cornerstone[1] > ystartCoordMax):
			ystartCoordMax = cornerstone[1]
		pillarheight = random.randint(5, 45)
		for y in range(0, pillarheight):
			utilityFunctions.setBlock(level, (options["Material"].ID,0), cornerstone[0], cornerstone[1]+y, cornerstone[2])
			if(y==pillarheight-1):
				# add y to our y coords, which will be used to determine building height for the roof
				ycoords.append(y)
	allYs = 0
	for ycoord in ycoords:
		allYs += ycoord
	yavg = allYs / 4
	midpointFloorHeight = midpointFloorHeight / 4
	# print("Average pillar height: ", yavg)
	return (yavg, ystartCoordMax, midpointFloorHeight)

# the walls of the building are generated each using independent ceullular automata. We look at the immediate neighborhood and take action
# cellular automata is done in 3 easy steps
# 1. intitialize with random block placement in the space
# 2. evaluate each cell, checking its neighbors to gauge changes
# 3. repeat 2 until satisfied
def generateWalls(level, floor, buildingHeightInfo, options):
	print "Generating walls"
	# actual automata is going to be simulated in a matrix (it's much faster than rendering it in minecraft)
	# first we should define the matrix properties (i.e. width and height)
	(width, boxheight, depth) = utilityFunctions.getBoxSize(floor)
	height = buildingHeightInfo[0]
	print "X walls"
	for k in range(2):
		# we have our matrix for CA, now lets do CA
		matrix = [[0 for x in range(width)] for y in range(height)]
		matrixnew = randomlyAssign(matrix, width, height)
		# do 3 generations
		for gen in range(0,2):
			# print "Generation ", gen
			matrixnew = cellularAutomataGeneration(matrixnew, width, height)
		#after generation is over, place the walls according to the wall matrix, starting at the floor
		for y in range(height):
			for x in range(1,width):
				if k==1:
					# print "boom 1"
					if matrixnew[y][x] == 1:
						utilityFunctions.setBlock(level, (options["Material"].ID, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.minz)
					else:
						utilityFunctions.setBlock(level, (20, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.minz)
				else:
					# print "boom 2"
					if matrixnew[y][x] == 1:
						utilityFunctions.setBlock(level, (options["Material"].ID, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.maxz)
					else:
						utilityFunctions.setBlock(level, (20, 0), floor.minx+x, buildingHeightInfo[2] + y, floor.maxz)
	print "Z Walls"
	for k in range(2):
		# we have our matrix for CA, now lets do CA
		matrix = [[0 for x in range(depth)] for y in range(height)]
		matrixnew = randomlyAssign(matrix, depth, height)

		# do 25 generations
		for gen in range(0,25):
			print "Generation ", gen
			matrixnew = cellularAutomataGeneration(matrixnew, depth, height)

		#after generation is over, place the walls according to the wall matrix, starting at the floor
		for y in range(height):
			for z in range(1,depth):
				if k==1:
					# print "boom 3"
					if matrixnew[y][z] == 1:
						utilityFunctions.setBlock(level, (options["Material"].ID, 0), floor.minx, buildingHeightInfo[2] + y, floor.minz+z)
					else:
						utilityFunctions.setBlock(level, (20, 0), floor.minx, buildingHeightInfo[2] + y, floor.minz+z)
				else:
					# print "boom 4"
					if matrixnew[y][z] == 1:
						utilityFunctions.setBlock(level, (options["Material"].ID, 0), floor.maxx, buildingHeightInfo[2] + y, floor.minz+z)
					else:
						utilityFunctions.setBlock(level, (20, 0), floor.maxx, buildingHeightInfo[2] + y, floor.minz+z)
def randomlyAssign(matrix, width, height):
	print 'randomly assigning to matrix'
	for j in range(height):
		for i in range(width):
			# print j,i
			matrix[j][i] = random.randint(0,2)
	return matrix

def cellularAutomataGeneration(matrix, width, height):
	for j in range(height):
		for i in range(width):
			# print j,i
			if j == 0 : #special case for bottom
				matrix[j][i] = decideCell(1, matrix[j+1][i])
			elif j == height-1 : #special case for top
				matrix[j][i] = decideCell(matrix[j-1][i], 1)
			else:
				matrix[j][i] = decideCell(matrix[j-1][i], matrix[j+1][i])
	return matrix

# the rules for cellular automata are as follows:
# look above and below me.
#	If one of my neighbors is 0, I have a 50% chance to be 0
# 	If both of my neighbors are 0, I am a 1
#	If both of my neighbors are 1, I am a 0
def decideCell(top, bottom):
	if top + bottom == 1:
		chance = random.randint(0, 100)
		if chance < 50:
			return 0
		else:
			return 1
	elif top + bottom == 0:
		return 1
	elif top + bottom == 2:
		return 0
# puts a cap on the building in question
# uses the floor to determine the celing size, and the buildingHeightInfo tuple
# to place it at the right level
def generateCeiling(level, floor, buildingHeightInfo, options):
	print "generating ceiling"
	for x in range(floor.minx, floor.maxx+1):
		for z in range(floor.minz, floor.maxz+1):
			utilityFunctions.setBlock(level, (options["Material"].ID, 0), x, buildingHeightInfo[2] + buildingHeightInfo[0], z)
			# scan all the blocks above me and make them air (all the way to maxy)
			for y in range(buildingHeightInfo[2] + buildingHeightInfo[0] + 1, 256):
				utilityFunctions.setBlock(level, (0, 0), x, y, z)
