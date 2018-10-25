import numpy as np
import utilityFunctions
from room import Room
from translator import Translator
import random

''' 
This module allows you to automatically design floors in buildings, with varying degrees of success in functionality!
A lot of these ideas came from this paper: http://graphics.tudelft.nl/~rval/papers/lopes.GAMEON10.pdf
'''
class FloorDesigner:
	
	# Designs the floor and converts a floorplan (2d array) back into a 3d floor
	def __init__(self, level, box, options):
		self.level = level
		self.box = box
		self.options = options

		# transform box space into 2d numpy array
		self.floor = self.transform_to_floor()

		# a few variables
		self.section_variance = 2
		self.room_count = 3
		self.rooms = []


	def build_floor(self):
		# place the floor down first
		self.place_floor()

		# build outer walls
		self.place_outer_walls()

		# create initial room positions
		self.initialize_rooms()

		# debug information
		# self.print_floor()

		# grow the rooms until none can grow anymore
		self.grow_rooms()

		# fix the walls to patch up weird growing
		self.fix_walls()

		# builds the door locations between rooms and on the outerwall
		self.build_doors()

		#debug information
		# self.print_floor()

		# translate self.floor from 2d numpy array into 3d Minecraft space
		translator = Translator(self.level, self.box, self.floor, self.options) 
		translator.translate_floor()


	def transform_to_floor(self):
		# changes 3d Minecraft space into 2d numpy array
		box_size = utilityFunctions.getBoxSize(self.box)
		floor = np.zeros((box_size[0], box_size[2]))
		return floor

	def place_floor(self):
		# puts the floor down
		# technically this should be in the translator, but I'm lazy
		for x in range(self.box.minx, self.box.maxx):
			for z in range(self.box.minz, self.box.maxz):
				utilityFunctions.setBlock(self.level, (5,0), x, self.box.miny, z)

	def print_floor(self):
		# debug stuff
		print(self.floor)
		print("\n\n")

	def initialize_rooms(self):
		# create initial room positions, checks to see if these positions have already been made, 
		# to avoid rooms being right on top of each other
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
		# puts the outerwalls down
		for x in range(0, self.floor.shape[0]):
			self.floor[x, 0] = -1
			self.floor[x, self.floor.shape[1] - 1] = -1
		for z in range(0, self.floor.shape[1]):
			self.floor[0, z] = -1
			self.floor[self.floor.shape[0] - 1, z] = -1
		# make corners something else, so we don't consider them for doors to the outside later
		self.floor[0,0] = 0
		self.floor[0, self.floor.shape[1] - 1] = 0
		self.floor[self.floor.shape[0] - 1, 0] = 0
		self.floor[self.floor.shape[0] - 1, self.floor.shape[1] - 1] = 0

	def grow_rooms(self):
		# begin to grow the rooms out using single-point growth
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

	def build_doors(self):
		# builds the doors. Checks to make sure that there is a wall nearby, 
		# so that it would make sense that there is a door there at all
		for x in range(1, self.floor.shape[0]-1):
			for z in range(1, self.floor.shape[1]-1):
				if self.floor[x, z] == 0:
					if self.floor[x, z - 1] == 0 or self.floor[x, z + 1] == 0:
						# check up and down
						self.floor[x, z] = -2
						self.floor[x, z - 1] = 0
						self.floor[x, z + 1] = 0
					elif self.floor[x - 1, z] == 0 or self.floor[x + 1, z] == 0:
						# check left and right
						self.floor[x, z] = -2
						self.floor[x - 1, z] = 0
						self.floor[x + 1, z] = 0
		self.build_outside_door()

	def build_outside_door(self):
		# builds one door to the outside. Corners are not considered (because they are '0's!)
		potential_doors = []
		for x in range(0, self.floor.shape[0]):
			for z in range(0, self.floor.shape[1]):
				if self.floor[x,z] == -1:
					potential_doors.append((x, z))
		outer_door = random.choice(potential_doors)
		self.floor[outer_door[0], outer_door[1]] = -2

	def fix_walls(self):
		''' 
		fixes weird wall behavior, for example:
		|1|0|
		|0|3|
		This doesn't look very aesthetically pleasing, so we try to fill one of those non-0 numbers into a 0
		'''
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