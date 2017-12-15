import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

# These are a few helpful functions we hope you find useful to use



# sets the block to the given blocktype at the designated x y z coordinate
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
def setBlock(level, (block, data), x, y, z):
	level.setBlockAt((int)(x),(int)(y),(int)(z), block)
    	level.setBlockDataAt((int)(x),(int)(y),(int)(z), data)

# sets the block to the given blocktype at the designated x y z coordinate IF the block is empty (air)
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
def setBlockIfEmpty(level, (block, data), x, y, z):
    tempBlock = level.blockAt((int)(x),(int)(y),(int)(z))
    if tempBlock == 0:
		setBlock(level, (block, data), (int)(x),(int)(y),(int)(z))

# sets every block to the given blocktype from the given x y z coordinate all the way down to ymin if the block is empty
# *params*
# level : the minecraft world level
# (block, data) : a tuple with block = the block id and data being a subtype
# x,y,z : the coordinate to set
# ymin: the minium y in which the iteration ceases
def setBlockToGround(level, (block, data), x, y, z, ymin):
    for iterY in xrange(ymin, (int)(y)):
    	setBlockIfEmpty(level, (block, data), (int)(x),(int)(iterY),(int)(z))


# Given an x an z coordinate, this will drill down a y column from box.maxy until box.miny and return a list of blocks
def drillDown(level, x, z, miny, maxy):
	blocks = []
	for y in xrange(maxy, miny, -1):
		blocks.append(level.blockAt(x, y, z))
		# print level.blockAt(x,y,z)
	return blocks
	
# returns a 2d matrix representing tree trunk locations on an x-z coordinate basis (bird's eye view) in the given box
# *params*
# level: the minecraft world level
# box: the selected subspace of the world
def treeMap(level, box):
	# Creates a 2d array containing z rows, each of x items, all set to 0
	w = abs(box.maxz - box.minz)
	h = abs(box.maxx - box.minx)
	treeMap = zeros((w,h))

	countx = box.minx
	countz = box.minz
	# iterate over the x dimenison of the mapping
	for x in range(h):
		# iterate over the z dimension of the mapping
		countz = box.minz
		for z in range(w):
			# drillDown at this location and get all the blocks in the y-column
			column = drillDown(level, countx, countz, box.miny, box.maxy)
			for block in column:
				# check if any block in this column is a wooden trunk block. If so, there is at this x-z coordinate
				if block == 17:
					treeMap[z][x] = 17
			print treeMap[z][x] ,
			countz += 1
		print ''
		countx += 1
	return treeMap


# returns the box size dimensions in x y and z
def getBoxSize(box):
	return (box.maxx - box.minx, box.maxy - box.miny, box.maxz - box.minz)

# returns an array of blocks after raytracing from (x1,y1,z1) to (x2,y2,z2)
# this uses Bresenham 3d algorithm, taken from a modified version written by Bob Pendleton  
def raytrace((x1, y1, z1), (x2, y2, z2)):
	output = []

	x2 -= 1
	y2 -= 1
	z2 -= 1

	i = 0
	dx = 0
	dy = 0
	dz = 0
	l = 0
	m = 0
	n = 0
	x_inc = 0
	y_inc = 0
	z_inc = 0
	err_1 = 0
	err_2 = 0
	dx2 = 0
	dy2 = 0
	dz2 = 0
	point = [x1,y1,z1]

	dx = x2 - x1
	dy = y2 - y1;
	dz = z2 - z1;
	x_inc = -1  if dx < 0 else 1
	l = abs(dx)
	y_inc = -1 if dy < 0 else 1
	m = abs(dy)
	z_inc = -1 if dz < 0 else 1
	n = abs(dz)
	dx2 = l << 1
	dy2 = m << 1
	dz2 = n << 1
    
	if l >= m and l >= n:
		err_1 = dy2 - l
		err_2 = dz2 - l
		for i in range(l):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[1] += y_inc
				err_1 -= dx2

			if err_2 > 0:
				point[2] += z_inc
				err_2 -= dx2

			err_1 += dy2
			err_2 += dz2
			point[0] += x_inc
        
	elif m >= l and m >= n:
		err_1 = dx2 - m
		err_2 = dz2 - m
		for i in range(m):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[0] += x_inc
				err_1 -= dy2

			if err_2 > 0:
				point[2] += z_inc
				err_2 -= dy2

			err_1 += dx2
			err_2 += dz2
			point[1] += y_inc
        
	else: 
		err_1 = dy2 - n
		err_2 = dx2 - n
		for i in range(n):
			np = (point[0], point[1], point[2])
			output.append(np)
			if err_1 > 0:
				point[1] += y_inc
				err_1 -= dz2

			if err_2 > 0:
				point[0] += x_inc
				err_2 -= dz2

			err_1 += dy2
			err_2 += dx2
			point[2] += z_inc

	np = (point[0], point[1], point[2])
	output.append(np)
	return output
