
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, floor
from random import *

from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Float, TAG_Double, TAG_String, TAG_Long, alphaMaterials, MCSchematic, MCLevel, BoundingBox

inputs = (
		("GOTHAM", "label"),
		("WALL:", alphaMaterials.Stone),
		("GLASS:", alphaMaterials.GlassPane),
		("FACADE VERTICAL:", alphaMaterials.BlockofQuartz),
		("FACADE HORIZONTAL:", alphaMaterials.Sandstone),
		("Building Size", 40),
		("Building Gap", 4),
		("Road Gap", 19),
		("Path Gap", 4),
		("abrightmoore@yahoo.com.au", "label"),
		("http://brightmoore.net", "label"),
)

def facadeSection(materials,size,windowsize):
	''' Builds a building wall section
	
		wwwwwwwwwwww <-- Roofline / crenelation
		########____
		## ## ##____
		## ## ##___o
		########__o
		## ## ##_o
		## ## ##_o
		########_o__

		^^^^^^^ ^^^^
	    windows central
	'''
	width, height, depth = size
	model = MCSchematic(shape=size)
	
	PreferredWidth,PreferredHeight = windowsize
	
	centralSectionWidth = width>>3 # 1/8th
	
#	windowsBox = BoundingBox((0,0,0),((width>>1)-centralSectionWidth,height,depth))
#	centralBox = BoundingBox((0,0,0),(centralSectionWidth,height,depth))

	# A window
	
	# Windows
	
	WINDOW = window((PreferredWidth,PreferredHeight,depth),materials)
	
	tileWindow(model,WINDOW)
	
	crenelationDepth = depth
	crenelationHeight = randint(1,crenelationDepth)
	crenelation(model,materials,(crenelationDepth,crenelationHeight))
	
	return model

def crenelation(level,materials,size):
	crenelationDepth, crenelationHeight = size
	width = level.Width
	depth = level.Length
	height = level.Height
	
	maxSpan = 5
	

	spanLength = randint(maxSpan>>1,maxSpan) # This is a design cache for the repeating pattern
	
	for y in xrange(height-1-crenelationHeight,height):
		heightHere = 1.0
		if (height-crenelationHeight-1) > 0:
			heightHere = 1.0-float((height-y)/(height-crenelationHeight-1))
		span = []
		for x in xrange(0,(level.Width>>1)+1): # Draw each half
			maxZ = randint(1,crenelationDepth)
			maxZ = heightHere*float(maxZ)
			maxZ = int(maxZ)
			if len(span) < maxSpan:
				span.append(maxZ)
			elif x == maxSpan:
				i = maxSpan-1
				while i >= 0:
					span.append(span[i]) # Copy in reverse order the crenelation design
					i -= 1
			else:
				maxZ = span[x%maxSpan] # Cached design here
			shapeFill(level,materials[2],(x,y,0),(x,y,maxZ))
			shapeFill(level,materials[2],(width-1-x,y,0),(width-1-x,y,maxZ))
				
		
	
def tileWindow(level,WINDOW):
	b=range(4096)
	b.remove(0) # @CodeWarrior0 and @Wout12345 explained how to merge schematics			
	#describe(WINDOW)
	y = 0
	while y < level.Height:
		x = 0
		while x < (level.Width)>>1:
			level.copyBlocksFrom(WINDOW, BoundingBox((0,0,0),(WINDOW.Width,WINDOW.Height,WINDOW.Length)),(x,y,0),b)			
			level.copyBlocksFrom(WINDOW, BoundingBox((0,0,0),(WINDOW.Width,WINDOW.Height,WINDOW.Length)),(level.Width-WINDOW.Width-x,y,0),b)
			x += WINDOW.Width
		y += WINDOW.Height

	

def getBlockFromOptions(options,label):
	return ( options[label].ID,
			 options[label].blockData
			)

def perform(level, box, options):
	b=range(4096)
	b.remove(0) # @CodeWarrior0 and @Wout12345 explained how to merge schematics			


	buildingSize = options["Building Size"]
	
	width = box.maxx-box.minx
	depth = box.maxz-box.minz
	height = box.maxy-box.miny
	
	x = 0
	
	cursor = 0
	while x+buildingSize < width:
		z = 0	
		while z+buildingSize < depth:
			print "Building "+str(x)+","+str(z)
			p1 = (buildingSize,randint(height>>1,height),buildingSize)
			buildingBox = BoundingBox((0,0,0),p1)
			buildingSchema = level.extractSchematic(BoundingBox((box.minx+x,box.miny,box.minz+z),p1))
			building(buildingSchema, buildingBox,options)
			level.copyBlocksFrom(buildingSchema, buildingBox, (box.minx+x, box.miny, box.minz+z ),b)
			z += buildingSize+options["Building Gap"]
		x += buildingSize+options["Building Gap"]
		cursor += 1
		if cursor%3 == 2:
			x += 2*options["Path Gap"] + options["Road Gap"]

	level.markDirtyBox(box)	
	
			
def building(originalLevel, originalBox, options):
	b=range(4096)
	b.remove(0) # @CodeWarrior0 and @Wout12345 explained how to merge schematics			

	level = originalLevel.extractSchematic(originalBox) # Working set
	width = originalBox.width
	height = originalBox.height
	depth = originalBox.length
	box = BoundingBox((0,0,0),(width,height,depth))
	materials = [getBlockFromOptions(options,"WALL:"),
				 getBlockFromOptions(options,"GLASS:"),
				 getBlockFromOptions(options,"FACADE VERTICAL:"),
				 getBlockFromOptions(options,"FACADE HORIZONTAL:"),
				]

	# Ground Floor

	# Windows - need to be consistent
	Fwidth = Factorise(width>>1)
	PreferredWidth = Fwidth[randint(0,(len(Fwidth)-1)>>2)]
	if PreferredWidth < 6:
		PreferredWidth = 6
	if PreferredWidth > 12:
		PreferredWidth = 12
	Fheight = Factorise(height)
	PreferredHeight = Fheight[randint(0,(len(Fheight)-1)>>2)]
	if PreferredHeight < 8:
		PreferredHeight = 8
		
	
	# Face of the building
	facadePart = 1
	facadeHeightCursor = 0
	facadeDepthCursor = 0
	scale = randint(1,5)
	originalFacadeDepth = 0
	while facadeHeightCursor < height: # Build the face of the building
		facadeHeight = (1+(facadePart-1)*scale)*randint(8,32) # How tall should this bit be?
		if facadeHeightCursor+facadeHeight >= height:
			facadeHeight = height-facadeHeightCursor # Truncate the top section to the box height
		print facadeHeight,facadeHeightCursor
		facadeDepth = randint(2,4)
		if facadeDepth > depth:
			facadeDepth = depth
		if facadePart == 1:
			originalFacadeDepth = facadeDepth
			FACADE = facadeSection(materials,(width-(facadeDepth<<1)-facadeDepthCursor,facadeHeight,facadeDepth),(PreferredWidth,facadeHeight-2))
		else:
			FACADE = facadeSection(materials,(width-(facadeDepth<<1)-facadeDepthCursor,facadeHeight,facadeDepth),(PreferredWidth,PreferredHeight))
		# print FACADE, level, facadeDepthCursor
		print facadeHeight,facadeHeightCursor, FACADE
		level.copyBlocksFrom(FACADE, BoundingBox((0,0,0),(FACADE.Width,FACADE.Height-1,FACADE.Length)), 
							 (box.minx+facadeDepth+facadeDepthCursor,box.miny+facadeHeightCursor,box.maxz-1-facadeDepthCursor-facadeDepth))
		print facadeHeight,facadeHeightCursor, FACADE, level
		facadeDepthCursor += 1 #facadeDepth
		facadePart +=1
		facadeHeightCursor += facadeHeight
	# Verticals
	if randint(1,100) > 60: # Verticals all the way up
		for x in xrange(facadeDepthCursor,width>>1):
			depthhere = randint(0,depth)
			if x%PreferredWidth == 0:
				for z in xrange(1,depthhere):
					shapeFill(level,materials[2%len(materials)],(x,0,level.Length-facadeDepthCursor-1),(x,height,level.Length-1))
					shapeFill(level,materials[2%len(materials)],(width-1-x,0,level.Length-facadeDepthCursor-1),(width-1-x,height,level.Length-1-facadeDepthCursor+depthhere))
	
	FACADE = level.extractSchematic(BoundingBox((0,0,box.maxz-1-facadeDepthCursor-originalFacadeDepth),(box.maxx,box.maxy,box.maxz-(box.maxz-1-facadeDepthCursor-originalFacadeDepth))))
	FACADE.flipEastWest()
	level.copyBlocksFrom(FACADE, BoundingBox((0,0,0),(FACADE.Width,FACADE.Height,FACADE.Length)), (box.minx, box.miny, box.minz),b)
	FACADE = level.extractSchematic(BoundingBox((0,0,0),(box.maxx,box.maxy,box.maxz)))
	FACADE.rotateLeft()
	level.copyBlocksFrom(FACADE, BoundingBox((0,0,0),(FACADE.Width,FACADE.Height,FACADE.Length)), (box.minx, box.miny, box.minz),b)
	shapeFill(level,materials[0%len(materials)],(0,0,0),(level.Width-1,0,level.Length-1)) # Ground floor
	
	p1 = (box.minx+facadeDepthCursor+originalFacadeDepth,height-5,box.minz+facadeDepthCursor+originalFacadeDepth)
	p2 = (width-1-1*(facadeDepthCursor+originalFacadeDepth),height-3,depth-1-1*(facadeDepthCursor+originalFacadeDepth))
	# print p1,p2, facadeHeightCursor,height,level
	shapeFill(level,materials[0%len(materials)],p1,p2) # Roof
	
	buttressHeight = randint(height>>1,height)
	buttress = MCSchematic(shape=(facadeDepthCursor+originalFacadeDepth+1,buttressHeight,facadeDepthCursor+originalFacadeDepth+1))
	shapeFill(buttress,materials[2%len(materials)],(0,0,0),(buttress.Width,buttress.Height,buttress.Length))
	level.copyBlocksFrom(buttress, BoundingBox((0,0,0),(buttress.Width,buttress.Height,buttress.Length)),(0,0,0))
	level.copyBlocksFrom(buttress, BoundingBox((0,0,0),(buttress.Width,buttress.Height,buttress.Length)),(level.Width-1-buttress.Width,0,0))
	level.copyBlocksFrom(buttress, BoundingBox((0,0,0),(buttress.Width,buttress.Height,buttress.Length)),(level.Width-1-buttress.Width,0,level.Length-1-buttress.Length))
	level.copyBlocksFrom(buttress, BoundingBox((0,0,0),(buttress.Width,buttress.Height,buttress.Length)),(0,0,level.Length-1-buttress.Length))
	originalLevel.copyBlocksFrom(level, box, (originalBox.minx, originalBox.miny, originalBox.minz ),b)


def Factorise(number):
	Q = []
	
	for iter in xrange(1,(int)(number+1)):
		p = (int)(number/iter)
		if number - (p * iter) == 0:
			if iter not in Q:
				Q.append(iter)
			if p not in Q:
				Q.append(p)

#	print 'Factors of %s are:' % (number)
#	for iter in Q:
#		print '%s,' % (iter)
	
	return Q
	
def setBlock(level,material,point):
	(x,y,z) = point
	(bID,bDATA) = material
	level.setBlockAt(x,y,z,bID)
	level.setBlockDataAt(x,y,z,bDATA)

def getBlock(level,point):
	(x,y,z) = point
	return (level.blockAt(x,y,z),level.blockDataAt(x,y,z))
	
def shapeFill(shape,material,p1,p2):
	#print p1,p2
	(x1,y1,z1) = p1
	(x2,y2,z2) = p2
	
	for x in xrange(x1,x2+1):
		for z in xrange(z1,z2+1):
			for y in xrange(y1,y2+1):
				setBlock(shape,material,(x,y,z))
				
def cloneSchematic(destination,source,pos):
	x1,y1,z1 = pos
	for y in xrange(0,source.Height):
		for z in xrange(0,source.Length):
			for x in xrange(0,source.Width):
				setBlock(destination,getBlock(source,(x,y,z)),((x+x1),(y+y1),(z+z1)))
				
def describe(schematic):
	width = schematic.Width
	height = schematic.Height
	depth = schematic.Length
	
	for y in xrange(0,height):
		for z in xrange(0,depth):
			row = ""
			for x in xrange(0,width):
				if schematic.blockAt(x,y,z) != 0:
					row = row+"#"
				else:
					row = row+" "
			print row
		print "--------\n"
		
def window(dim,materials):
	''' Create a window design of the specified size
	'''
	model = MCSchematic(shape=dim) # This will be returned. A model of a window width and height-wise with depth features
	(x,y,z) = dim
	depth = z
	width = x
	height = y
	heightHalf = y>>1
	heightQtr = heightHalf>>1

	# Design half the window and mirror it width-wise
	widthHalf = x>>1
	if widthHalf<<1 < width:
		widthHalf += 1 # If the width is odd then there is a centre position that needs to be drawn otherwise there would be a gap
	shapeWindowHalf = MCSchematic(shape=(widthHalf,height,depth))
	shapeFill(shapeWindowHalf,materials[0],(0,0,0),(widthHalf-1,height-1,0))
	# A window is glass in the centre, Stone with vertical design elements outside that, and window sill and top
	GLASSTOP = randint(heightQtr,heightHalf) # Distances from the centre
	GLASSBOT = randint(heightQtr,heightHalf)
	GLASSEDGE = (width>>1)-1 #randint(width>>2,(width>>1))
	if GLASSEDGE >= (width>>1)-1:
		GLASSEDGE -= 2
		if GLASSEDGE < 1:
			GLASSEDGE = 2
	if GLASSTOP >= heightHalf-1:
		GLASSTOP -= 2
	# print GLASSEDGE,shapeWindowHalf
	# Glass
	shapeFill(shapeWindowHalf,materials[1%len(materials)],(0,GLASSBOT,0),(GLASSEDGE,heightHalf+GLASSTOP,0))
	
	# Horizontals
	for y in xrange(0,heightHalf-GLASSBOT):
		depthhere = randint(0,depth)
		for z in xrange(1,depthhere):
			shapeFill(shapeWindowHalf,materials[3%len(materials)],(0,y,z),(widthHalf,y,z))
	
	for y in xrange(heightHalf+GLASSTOP,height):
		depthhere = randint(0,depth)
		for z in xrange(1,depthhere):
			shapeFill(shapeWindowHalf,materials[3%len(materials)],(0,y,z),(widthHalf,y,z))

	
	# Verticals
	for x in xrange(GLASSEDGE,width):
		depthhere = randint(0,depth)
		if x%width-1 == 0:
			depthhere = randint(1,depth)
		if depthhere > 0:
			shapeFill(shapeWindowHalf,materials[2%len(materials)],(x,0,0),(x,height-1,depthhere))


	# Render
	b=range(4096)
	b.remove(0) # @CodeWarrior0 and @Wout12345 explained how to merge schematics			
	model.copyBlocksFrom(shapeWindowHalf, BoundingBox((0,0,0),(widthHalf,height,depth)), (widthHalf-(width%2),0,0),b)
	# cloneSchematic(model,shapeWindowHalf,(0,0,0))
	#describe(model)
	shapeWindowHalf.flipNorthSouth()
	
	model.copyBlocksFrom(shapeWindowHalf, BoundingBox((0,0,0),(widthHalf,height,depth)), (0,0,0),b)	
	
	return model