import numpy as np
import utilityFunctions
from room import Room
from translator import Translator
import random

class FloorDesigner:
	
	# Designs the floor and converts a floorplan (2d array) back into a 3d floor
	def __init__(self, level, box, options):
		self.level = level
		self.box = box
		self.options = options
		self.floor = self.transform_to_floor()
		# self.location = [1,1]
		# self.legal_moves = []

		self.section_variance = 2
		self.room_count = 3
		self.rooms = []


	def build_floor(self):
		self.place_floor()
		self.place_outer_walls()
		# self.print_floor()
		# self.public_private_sectioning()
		self.initialize_rooms()

		self.print_floor()

		self.grow_rooms()
		self.fix_walls()

		self.build_doors()
		self.print_floor()

		translator = Translator(self.level, self.box, self.floor, self.options) 
		translator.translate_floor()


	def transform_to_floor(self):
		box_size = utilityFunctions.getBoxSize(self.box)
		floor = np.zeros((box_size[0], box_size[2]))
		return floor

	def place_floor(self):
		for x in range(self.box.minx, self.box.maxx):
			for z in range(self.box.minz, self.box.maxz):
				utilityFunctions.setBlock(self.level, (5,0), x, self.box.miny, z)

	# def dig(self):
	# 	self.floor[self.location[0], self.location[1]] = 0

	# def move(self):
	# 	self.get_legal_moves()
	# 	move = random.choice(self.legal_moves)
	# 	self.location = [x + y for x, y in zip(self.location, move)]

	# def get_legal_moves(self):
	# 	self.legal_moves = []
	# 	if self.location[0] > 1:
	# 		self.legal_moves.append([-1, 0])
	# 	if self.location[0] < self.floor.shape[0] - 2:
	# 		self.legal_moves.append([1, 0])
	# 	if self.location[1] > 1:
	# 		self.legal_moves.append([0, -1])
	# 	if self.location[1] < self.floor.shape[1] - 2:
	# 		self.legal_moves.append([0, 1])

	def print_floor(self):
		print(self.floor)
		print("\n\n")


	# def public_private_sectioning(self):
	# 	x_or_z = random.randint(0, 1)
	# 	print(x_or_z)
	# 	if x_or_z == 0:
	# 		x_bisect = random.randint(self.floor.shape[0] / 2 - self.section_variance, self.floor.shape[0] / 2 + self.section_variance)
	# 		for z in range(0, self.floor.shape[1]):
	# 			self.floor[x_bisect, z] = 0
	# 	else:
	# 		z_bisect = random.randint(self.floor.shape[1] / 2 - self.section_variance, self.floor.shape[1] / 2 + self.section_variance)
	# 		for x in range(0, self.floor.shape[0]):
	# 			self.floor[x, z_bisect] = 0

	def initialize_rooms(self):
		initial_positions = []
		for i in range(0, self.room_count):
			initial_position = (random.randint(2, self.floor.shape[0] - 2), random.randint(2, self.floor.shape[1] - 2))
			while initial_position in initial_positions:
				initial_position = (random.randint(2, self.floor.shape[0] - 2), random.randint(2, self.floor.shape[1] - 2))
			
			# append this initial position, as well as all adjacent positions (prevents rooms from starting too close)
			for k in range(-2, 3):
				for j in range(-2, 3):
					initial_positions.append((initial_position[0] + k, initial_position[1] + j))

			room = Room(initial_position, i + 1)
			
			self.rooms.append(room)
			self.floor[initial_position[0], initial_position[1]] = room.number
			self.floor[initial_position[0] - 1, initial_position[1]] = room.number
			self.floor[initial_position[0], initial_position[1] - 1] = room.number
			self.floor[initial_position[0] - 1, initial_position[1] - 1] = room.number
		
	def place_outer_walls(self):
		for x in range(0, self.floor.shape[0]):
			self.floor[x, 0] = -1
			self.floor[x, self.floor.shape[1] - 1] = -1
		for z in range(0, self.floor.shape[1]):
			self.floor[0, z] = -1
			self.floor[self.floor.shape[0] - 1, z] = -1
		# make corners something else
		self.floor[0,0] = 0
		self.floor[0, self.floor.shape[1] - 1] = 0
		self.floor[self.floor.shape[0] - 1, 0] = 0
		self.floor[self.floor.shape[0] - 1, self.floor.shape[1] - 1] = 0

	def grow_rooms(self):
		# begin to grow the rooms out using rectangular growth
		growable_rooms = self.get_growable_rooms()
		while growable_rooms:
			# while moves are possible, select a possible move and do it
			room_to_grow = random.choice(growable_rooms)
			room_to_grow.grow(self.floor)

			# refresh which rooms are growable
			growable_rooms = self.get_growable_rooms()
		print("*** done growing ***")

	def refresh_moves(self):
		for room in self.rooms:
			room.check_moves(self.floor)

	def get_growable_rooms(self):
		self.refresh_moves()
		
		growable_rooms = []
		for room in self.rooms:
			if room.possible_moves:
				growable_rooms.append(room)
		return growable_rooms

	def fix_rooms(self):
		for x in range(1, self.floor.shape[0]-1):
			for z in range(1, self.floor.shape[1]-1):
				if self.floor[x, z] > 0 and self.is_surrounded((x, z), 0) > 2:
					self.floor[x, z] = 0

	def is_surrounded(self, block, x):
		# checks to see if a block is surrounded by x's or 2 x's and a -1
		count = 0
		if self.floor[block[0], block[1] - 1] == x or self.floor[block[0], block[1] - 1] == -1:
			count += 1
		if self.floor[block[0], block[1] + 1] == x or self.floor[block[0], block[1] + 1] == -1:
			count += 1
		if self.floor[block[0] - 1, block[1]] == x or self.floor[block[0] - 1, block[1]] == -1:
			count += 1
		if self.floor[block[0] + 1, block[1]] == x or self.floor[block[0] + 1, block[1]] == -1:
			count += 1
		return count


	def build_doors(self):
		for x in range(1, self.floor.shape[0]-1):
			for z in range(1, self.floor.shape[1]-1):
				if self.floor[x, z] == 0:
					# check up and down
					if self.floor[x, z - 1] == 0 or self.floor[x, z + 1] == 0:
						self.floor[x, z] = -2
						self.floor[x, z - 1] = 0
						self.floor[x, z + 1] = 0
					elif self.floor[x - 1, z] == 0 or self.floor[x + 1, z] == 0:
						self.floor[x, z] = -2
						self.floor[x - 1, z] = 0
						self.floor[x + 1, z] = 0
		self.build_outside_door()

	def build_outside_door(self):
		potential_doors = []
		for x in range(0, self.floor.shape[0]):
			for z in range(0, self.floor.shape[1]):
				if self.floor[x,z] == -1:
					potential_doors.append((x, z))
		outer_door = random.choice(potential_doors)
		self.floor[outer_door[0], outer_door[1]] = -2

	def fix_walls(self):
		empties = []
		for x in range(1, self.floor.shape[0] - 1):
			for z in range(1, self.floor.shape[1]-1):
				if self.floor[x, z] > 0:
					empties.append((x, z))

		random.shuffle(empties)
		for block in empties:
			if self.floor[block[0] + 1, block[1] + 1] > 0 and (self.floor[block[0], block[1] + 1] < 1) and (self.floor[block[0] + 1, block[1]] < 1):
				self.floor[block[0], block[1]] = 0
			elif self.floor[block[0] - 1, block[1] - 1] > 0 and (self.floor[block[0], block[1] - 1] < 1) and (self.floor[block[0] - 1, block[1]] < 1):
				self.floor[block[0], block[1]] = 0
			elif self.floor[block[0] - 1, block[1] + 1] > 0 and (self.floor[block[0], block[1] + 1] < 1) and (self.floor[block[0] - 1, block[1]] < 1):
				self.floor[block[0], block[1]] = 0
			elif self.floor[block[0] + 1, block[1] - 1] > 0 and (self.floor[block[0], block[1] - 1] < 1) and (self.floor[block[0] + 1, block[1]] < 1):
				self.floor[block[0], block[1]] = 0

