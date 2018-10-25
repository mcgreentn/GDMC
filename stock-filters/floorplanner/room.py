import numpy as np
import random

class Room:
	# Holds information about the floor plan
	def __init__(self, origin, number):
		self.origin = origin
		self.number = number
		self.min_x = 1000
		self.min_z = 1000
		self.max_x = -1
		self.max_z = -1
		self.possible_moves = []

	def grow(self, floor):
		# pick a move and expand
		move = random.choice(self.possible_moves)
		floor[move[0], move[1]] = self.number

	def check_moves(self, floor):
		self.possible_moves = []
		for x in range(0, floor.shape[0]):
			for z in range(0, floor.shape[1]):
				if floor[x,z] == self.number:
					print("x:{} z:{}".format(x, z))
					# up
					if self.is_growth_applicable(floor, (x, z - 1)):
						self.possible_moves.append((x, z - 1))
					# down
					if self.is_growth_applicable(floor, (x, z + 1)):
						self.possible_moves.append((x, z + 1))
					# left
					if self.is_growth_applicable(floor, (x - 1, z)):
						self.possible_moves.append((x - 1, z))
					# right
					if self.is_growth_applicable(floor, (x + 1, z)):
						self.possible_moves.append((x + 1, z))
		print(self.possible_moves)

	def is_growth_applicable(self, floor, coord):
		if floor[coord[0], coord[1]] != 0:
			# same tile
			# print("{} is not 0".format(coord))
			return False
		elif floor[coord[0], coord[1] - 1] != 0 and floor[coord[0], coord[1] - 1] != -1 and floor[coord[0], coord[1] - 1] != self.number:
			# up
			# print("{} is {}".format((coord[0], coord[1] - 1), floor[coord[0], coord[1] - 1]))
			return False
		elif floor[coord[0], coord[1] + 1] != 0 and floor[coord[0], coord[1] + 1] != -1 and floor[coord[0], coord[1] + 1] != self.number:
			# down
			# print("{} is {}".format((coord[0], coord[1] + 1), floor[coord[0], coord[1] + 1]))
			return False
		elif floor[coord[0] - 1, coord[1]] != 0 and floor[coord[0] - 1, coord[1]] != -1 and floor[coord[0] - 1, coord[1]] != self.number:
			# left
			# print("{} is {}".format((coord[0] - 1, coord[1]), floor[coord[0] - 1, coord[1]]))			
			return False
		elif floor[coord[0] + 1, coord[1]] != 0 and floor[coord[0] + 1, coord[1]] != -1 and floor[coord[0] + 1, coord[1]] != self.number:
			# right
			# print("{} is {}".format((coord[0] + 1, coord[1]), floor[coord[0] + 1, coord[1]]))						
			return False
		# print("{} is growth applicable!".format(coord))
		return True

	
	def border_refresh(self, floor):
		# refresh the min and max dimensions of this room, so we can check moves for it
		borders = []
		for x in range(0, floor.shape[0]):
			for z in range(0, floor.shape[1]):
				if floor[x,z] == self.number:
					if x > self.max_x:
						self.max_x = x
					if x < self.min_x:
						self.min_x = x
					if z > self.max_z:
						self.max_z = z
					if z < self.min_z:
						self.min_z = z
		print(str(self.min_x) + ", " + str(self.min_z) + " :: " + str(self.max_x) + ", " + str(self.max_z))

