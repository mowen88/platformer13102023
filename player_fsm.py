import pygame
from settings import *

class Fall:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if player.collide_ladders() and player.vel.y > 0:
			return OnLadderIdle(player)

		if not player.alive:
			return Death(player)

		if ACTIONS['right_click']:
			player.jump_buffer_active = True
			ACTIONS['right_click'] = False
			if player.jump_counter > 0:
				if player.cyote_timer < player.cyote_timer_threshold:
					return Jump(player)
				else:
					return DoubleJump(player)

		if player.on_ground:
			if player.jump_buffer > 0:
				player.jump_counter = 1
				return Jump(player)
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

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

		if ACTIONS['up'] and player.collide_ladders():
			return OnLadderIdle(player)

		if abs(player.vel.x) >= 0.1:
			return Move(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('idle', 0.25 * dt)

class OnLadderIdle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.on_ground = True

		player.scene.gun_sprite.kill()

	def state_logic(self, player):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			player.acc.y = -player.acc_rate * 0.5
			return OnLadderMove(player)
		elif keys[pygame.K_DOWN]:
			player.acc.y = player.acc_rate * 0.5
			return OnLadderMove(player)
		else:
			player.acc.y = 0

		if not player.alive:
			return Death(player)

		if not player.collide_ladders():
			player.scene.create_player_gun()
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.ladder_physics(dt)

		player.animate('on_ladder_idle', 0.25 * dt, False)

class OnLadderMove:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0
		player.on_ground = True

	def state_logic(self, player):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			player.acc.y = -player.acc_rate * 0.5
		elif keys[pygame.K_DOWN]:
			player.acc.y = player.acc_rate * 0.5
		else:
			player.acc.y = 0

		if player.vel.magnitude() <= 0.1:
			return OnLadderIdle(player)

		if not player.alive:
			return Death(player)

		if not player.collide_ladders():
			player.scene.create_gun(player)
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.ladder_physics(dt)

		player.animate('on_ladder_move', 0.25 * dt)

class Move:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

		if ACTIONS['up'] and player.collide_ladders():
			return OnLadderIdle(player)
			
		if not ACTIONS['left'] and not ACTIONS['right'] or (ACTIONS['left'] and ACTIONS['right']):
			return Skid(player)

	def update(self, player, dt):
	
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('run', 0.25 * dt)

class Skid:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

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

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

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

class Jump(Fall):
	def __init__(self, player):

		player.frame_index = 0
		player.jump(player.jump_height)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)


		if ACTIONS['right_click'] and player.jump_counter > 0:
			ACTIONS['right_click'] = False
			return DoubleJump(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('jump', 0.25 * dt, False)

class DoubleJump(Fall):
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