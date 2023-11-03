import pygame
from settings import *

class Fall:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return AirDash(player)

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
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('fall', 0.2 * dt, False)

class Idle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return Roll(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if player.move['right']:
			player.acc.x += 0.5
			player.facing = 0
			return Move(player)

		elif player.move['left']:
			player.acc.x -= 0.5
			player.facing = 1
			return Move(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('idle', 0.2 * dt)

class Move:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return Roll(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if not (player.move['right'] or player.move['left']) and abs(player.vel.x) <= 0.1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)

		if (player.vel.x > 0 and not player.move['right']) or (player.vel.x < 0 and not player.move['left']):
			player.animate('skid', 0.2 * dt)
		else:
			player.animate('run', 0.2 * dt)

class Landing:
	def __init__(self, player):

		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return Roll(player)

		if ACTIONS['up']:
			ACTIONS['up'] = False
			return Jumping(player)

		if player.frame_index > len(player.animations['land'])-1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('land', 0.2 * dt)

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

		player.animate('death', 0.2 * dt)

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

		player.animate('death', 0.2 * dt, False)

class Jumping(Fall):
	def __init__(self, player):

		player.jump(player.jump_height)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return AirDash(player)

		if ACTIONS['up'] and player.jump_counter > 0:
			ACTIONS['up'] = False
			return DoubleJumping(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('fall', 0.2 * dt)

class DoubleJumping(Fall):
	def __init__(self, player):

		player.jump_counter = 0
		player.jump(player.jump_height)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)

		if ACTIONS['left_click']:
			ACTIONS['left_click'] = False
			return AirDash(player)

	def update(self, player, dt):
		
		player.acc.x = 0
		player.move_logic()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('double_jump', 0.2 * dt)
		
class Roll(Fall):
	def __init__(self, player):
		
		self.speed = 10 * self.direction(player)
		player.vel.x = self.speed

	def direction(self, player):
		if player.facing == 0:
			return 1
		else:
			return -1

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if abs(player.vel.x) <= 5 and (ACTIONS['left'] or ACTIONS['right']):
			return Move(player)

		if abs(player.vel.x) <= 0.5:
			return Idle(player)


	def update(self, player, dt):

		player.acc.x = 0

		player.vel.x = self.speed
		self.speed -= self.direction(player) * dt * 0.4
		player.physics_x(dt)

		player.animate('double_jump', 0.2 * dt)

class AirDash(Roll):

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if abs(player.vel.x) <= 5 and (ACTIONS['left'] or ACTIONS['right']):
			return Fall(player)

		if abs(player.vel.x) <= 0.5:
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0

		player.vel.x = self.speed
		self.speed -= self.direction(player) * dt * 0.4
		player.physics_x(dt)

		player.animate('idle', 0.2 * dt)