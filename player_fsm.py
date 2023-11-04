import pygame
from settings import *

class Fall:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['up']:
			player.jump_buffer_active = True
			ACTIONS['up'] = False
			if player.jump_counter > 0:
				if player.cyote_timer < player.cyote_timer_threshold:
					return Jumping(player)
				else:
					return DoubleJumping(player)

		if player.on_ground:
			if player.jump_buffer > 0:
				player.jump_counter = 1
				return Jumping(player)
			else:
				return Landing(player)

	def update(self, player, dt):
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('fall', 0.25 * dt, False)

class Idle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if abs(player.vel.x) >= 0.1:
			return Move(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('idle', 0.25 * dt)

class Move:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if not ACTIONS['left'] and not ACTIONS['right']:
			return Skid(player, player.vel.x)

	def update(self, player, dt):
	
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('run', 0.25 * dt)

class Skid:
	def __init__(self, player, vel_x):
		
		player.jump_counter = 1
		player.frame_index = 0
		self.vel_x = vel_x

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if abs(player.vel.x) <= 0.1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('skid', 0.25 * dt, False)

class Landing:
	def __init__(self, player):

		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if player.frame_index > len(player.animations['land'])-1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('land', 0.25 * dt)

class WakeUp:
	def __init__(self, player):

		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):
		if player.frame_index > len(player.animations['death'])-1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('death', 0.25 * dt)

class Death(Fall):
	def __init__(self, player):
		
		self.timer = 120

	def state_logic(self, player):
		if self.timer <= 0:
			player.zone.restart_zone(player.zone.name)

	def update(self, player, dt):
		self.timer -= dt

		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('death', 0.25 * dt, False)

class Jumping(Fall):
	def __init__(self, player):

		player.frame_index = 0
		player.jump(player.jump_height)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)


		if ACTIONS['up'] and player.jump_counter > 0:
			ACTIONS['up'] = False
			return DoubleJumping(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('jump', 0.25 * dt, False)

class DoubleJumping(Fall):
	def __init__(self, player):

		player.jump_counter = 0
		player.frame_index = 0
		player.jump(player.jump_height)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)


	def update(self, player, dt):
		
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('double_jump', 0.25 * dt, False)