import time # for timing
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *

import utilityFunctions as utilityFunctions
from floor_designer import FloorDesigner

inputs = (
	("FloorPlanModule", "label"),
	("Creator: Michael C Green", "label"),
	("Floor_Material", alphaMaterials.WoodPlanks),
	("Wall_Material", alphaMaterials.Wood)
	)

# MAIN SECTION #
# 1: the level (aka the minecraft world). 2: the selected box from mcedit. 3: User defined inputs from mcedit
def perform(level, box, options):
	designer = FloorDesigner(level, box, options)
	designer.build_floor()

