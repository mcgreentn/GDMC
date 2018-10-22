import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions as utilityFunctions

inputs = (
	("FloorPlanModule", "label"),
	("Creator: Michael Green", "label"),
	)

# MAIN SECTION #
# 1: the level (aka the minecraft world). 2: the selected box from mcedit. 3: User defined inputs from mcedit
def perform(level, box, options):
	plan_floor(level, box)

def plan_floor(level, box):
	# this method uses a digger agent with room placement abilities, methods defined below
	# make a floor, then build walls on top of that
	place_floor(level, box)
	digger(level, box)
def place_floor(level, box):
	for x in range(box.minx, box.maxx):
		for z in range(box.minz, box.maxz):
			print(x, box.miny+1, z)
			utilityFunctions.setBlock(level, (5,0), x, box.miny, z)

def digger(level, box):
	floor = transform_to_floor(box)

def transform_to_floor(box):
	box_size = utilityFunctions.getBoxSize(box)
	
# def advance_digger(floor):


# def place_room(floor):
