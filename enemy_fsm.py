import pygame
from settings import *

class Fall:
	def __init__(self, enemy):
		
		enemy.frame_index = 0

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if enemy.on_ground:
			return Landing(enemy)

	def update(self, enemy, dt):
		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('fall', 0.25 * dt, False)

class Idle:
	def __init__(self, enemy):
		
		enemy.frame_index = 0

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if not enemy.on_ground:
			return Fall(enemy)

		if abs(enemy.vel.x) >= 0.1:
			return Move(enemy)

	def update(self, enemy, dt):

		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)
		enemy.animate('idle', 0.25 * dt)

class Move:
	def __init__(self, enemy):
		
		enemy.frame_index = 0

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if not enemy.on_ground:
			return Fall(enemy)

		if abs(enemy.vel.x) <= 0.1:
			return Idle(enemy)

	def update(self, enemy, dt):
	
		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('run', 0.25 * dt)


class Landing:
	def __init__(self, enemy):

		enemy.frame_index = 0

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(enemy)

		if enemy.frame_index > len(enemy.animations['land'])-1:
			return Idle(enemy)

	def update(self, enemy, dt):

		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('land', 0.25 * dt)

class Death(Fall):
	def __init__(self, enemy):
		
		self.timer = 120

	def state_logic(self, enemy):
		if self.timer <= 0:
			enemy.zone.restart_zone(enemy.zone.name)

	def update(self, enemy, dt):
		self.timer -= dt

		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('death', 0.25 * dt, False)

class Jumping(Fall):
	def __init__(self, enemy):

		enemy.frame_index = 0
		enemy.jump(enemy.jump_height)

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if enemy.vel.y > 0:
			return Fall(enemy)

	def update(self, enemy, dt):

		enemy.acc.x = 0

		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('jump', 0.25 * dt, False)