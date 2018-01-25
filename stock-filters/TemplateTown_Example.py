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


