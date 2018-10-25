import utilityFunctions
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox

class Translator:

	def __init__(self, level, box, floor, options):
		self.level = level
		self.box = box
		self.floor = floor
		self.options = options

	def translate_floor(self):
		# translates the floor into minecraft blocks. Doors get two conditions, one for the door itself, and one for the wall above it
		for y in range(1, utilityFunctions.getBoxSize(self.box)[1]):
			for x in range(0, self.floor.shape[0]):
				for z in range(0, self.floor.shape[1]):
					if self.floor[x, z] == 0 or self.floor[x, z] == -1:
						utilityFunctions.setBlock(self.level, (self.options["Wall_Material"].ID, 0), self.box.minx + x, self.box.miny + y, self.box.minz + z)
					elif self.floor[x, z] == -2 and y < 3:
						# this is a door, figure out which direction it goes
						self.translate_door((x, z), y)
					elif self.floor[x, z] == -2 and y >= 3:
						utilityFunctions.setBlock(self.level, (self.options["Wall_Material"].ID, 0), self.box.minx + x, self.box.miny + y, self.box.minz + z)

		# self.make_ceiling()

	def make_ceiling(self):
		for x in range(1, self.floor.shape[0] - 1):
			for z in range(1, self.floor.shape[1] - 1):
				utilityFunctions.setBlock(self.level, (self.options["Floor_Material"].ID, 0), self.box.minx + x, self.box.maxy-1, self.box.minz + z)


	def translate_door(self, coord, y):
		''' 
		A very lazy implementation of this, by brute forcing a try catch in there to stop out-of-bounds exceptions because of the outer door
		Someone much better than I will hopefully one day come along and fix my broken mess of code :)
		'''
		try:
			# up and down
			if self.floor[coord[0], coord[1] - 1] != -1 and self.floor[coord[0], coord[1] - 1] != 0 and self.floor[coord[0], coord[1] + 1] != -1 and self.floor[coord[0], coord[1] + 1] != 0:
				# basically "are there any walls above or below me?"
				# if not, the door will go up and down
				if y == 1:
					# bottom door, north-south
					utilityFunctions.setBlock(self.level, (64, 1), (self.box.minx + coord[0]), (self.box.miny + y), (self.box.minz + coord[1]))
				else:
					# top door, north-south
					utilityFunctions.setBlock(self.level, (64, 9), self.box.minx + coord[0], self.box.miny + y, self.box.minz + coord[1])
			# left and right
			else:
				if y == 1:
					utilityFunctions.setBlock(self.level, (64, 0), self.box.minx + coord[0], self.box.miny + y, self.box.minz + coord[1])
				else:
					utilityFunctions.setBlock(self.level, (64, 8), self.box.minx + coord[0], self.box.miny + y, self.box.minz + coord[1])
		except:
			if y == 1:
				# bottom door, north-south
				utilityFunctions.setBlock(self.level, (64, 1), (self.box.minx + coord[0]), (self.box.miny + y), (self.box.minz + coord[1]))
			else:
				# top door, north-south
				utilityFunctions.setBlock(self.level, (64, 9), self.box.minx + coord[0], self.box.miny + y, self.box.minz + coord[1])