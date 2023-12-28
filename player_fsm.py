import pygame
from settings import *

class Hold:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):
		if player.scene.fade_surf.alpha < 255 and not player.scene.exiting:
			return Idle(player)

	def update(self, player, dt):
		player.acc.x = 0
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('idle', 0.25 * dt, False)

class Death:
	def __init__(self, player):
		
		player.scene.create_particle('chunk',player.rect.center)
		player.scene.drawn_sprites.remove(player)
		player.gun_sprite.kill()
		self.timer = 100

	def state_logic(self, player):
		if self.timer < 0:
			player.scene.respawn()

	def update(self, player, dt):
		self.timer -= dt



class Fall:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if player.collide_ladders() and player.vel.y > 0:
			return OnLadderIdle(player)

		if not player.alive:
			return Death(player)

		if ACTIONS['left_click']:
			player.fire()

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
			elif ACTIONS['down']:
				return Crouch(player)
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
		player.acc_rate = 0.4
		player.drop_through = False

	def state_logic(self, player):

		if player.scene.exiting:
			return Hold(player)

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['left_click']:
			player.fire()

		if ACTIONS['down'] and not player.drop_through:
			return Crouch(player)

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

		player.get_on_ground()
		player.exit_scene()
		
class Crouch:
	def __init__(self, player):
		
		player.frame_index = 0

		# slow the player if moving when crouched
		player.acc_rate = 0.2

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not ACTIONS['down'] and not player.got_headroom() or player.vel.y > 1:
			return Idle(player)

		if ACTIONS['left_click']:
			player.fire()

		if ACTIONS['right_click']:
			player.drop_through = True
			ACTIONS['right_click'] = False

		if abs(player.vel.x) >= 0.1:
			return CrouchMove(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)

		# slow the player if moving when crouched
		# player.vel.x = player.vel.x / 2 * dt

		player.physics_y(dt)
		player.animate('crouch', 0.2 * dt, False)

		player.get_on_ground()

class CrouchMove:
	def __init__(self, player):
		
		player.frame_index = 0

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not ACTIONS['down'] and not player.got_headroom() or player.vel.y > 1:
			player.acc_rate = 0.4
			return Idle(player)

		if ACTIONS['left_click']:
			player.fire()

		if ACTIONS['right_click']:
			player.drop_through = True
			ACTIONS['right_click'] = False

		if abs(player.vel.x) < 0.1:
			return Crouch(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)
		player.animate('crouch', 0.25 * dt, False)
		player.get_on_ground()

class Move:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if ACTIONS['scroll_up']:
			player.change_weapon(1)
			ACTIONS['scroll_up'] = False
		elif ACTIONS['scroll_down']:
			player.change_weapon(-1)
			ACTIONS['scroll_down'] = False

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['left_click']:
			player.fire()

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

		if ACTIONS['up'] and player.collide_ladders():
			return OnLadderIdle(player)

		if ACTIONS['down']:
			return Crouch(player)
			
		if not ACTIONS['left'] and not ACTIONS['right'] or (ACTIONS['left'] and ACTIONS['right']):
			return Skid(player)

	def update(self, player, dt):

		player.get_on_ground()
		
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('run', 0.25 * dt)

class OnLadderIdle:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.on_ground = True

		# remove gun sprite from player when using ladder
		player.gun_sprite.kill()

		# stop auto weapons firing
		ACTIONS['left_click'] = False

	def state_logic(self, player):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			player.acc.y = -player.acc_rate * 0.5
			
		elif keys[pygame.K_DOWN]:
			player.acc.y = player.acc_rate * 0.5
			
		else:
			player.acc.y = 0

		if player.vel.magnitude() >= 0.1:
			return OnLadderMove(player)

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
			player.scene.create_player_gun()
			return Fall(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.ladder_physics(dt)

		player.animate('on_ladder_move', 0.25 * dt)

class Skid:
	def __init__(self, player):
		
		player.jump_counter = 1
		player.frame_index = 0

	def state_logic(self, player):

		if player.scene.exiting:
			return Hold(player)

		if not player.alive:
			return Death(player)

		if not player.on_ground:
			return Fall(player)

		if ACTIONS['left_click']:
			player.fire()

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
		player.exit_scene()
	
class Landing:
	def __init__(self, player):

		player.jump_counter = 1
		player.frame_index = 0
		player.scene.create_particle('landing', player.hitbox.midbottom)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if ACTIONS['left_click']:
			player.fire()

		if ACTIONS['right_click']:
			ACTIONS['right_click'] = False
			return Jump(player)

		if player.frame_index > len(player.animations[SAVE_DATA['armour_type']]['land'])-1:
			return Idle(player)

	def update(self, player, dt):

		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('land', 0.25 * dt)


class Jump(Fall):
	def __init__(self, player):

		player.frame_index = 0
		player.jump(player.jump_height)
		player.scene.create_particle('jump', player.hitbox.midbottom)

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		if player.vel.y > 0:
			return Fall(player)

		if ACTIONS['left_click']:
			player.fire()

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
		self.gun = player.gun
		player.scene.create_particle('double_jump', player.hitbox.midbottom)

		# remove gun sprite from player when double jumping
		player.gun_sprite.kill()

	def state_logic(self, player):

		if not player.alive:
			return Death(player)

		# self.gun is the gun you have before the double jump, and comparing it with a new one if you collected one while double jumping 
		if player.vel.y > 0:
			if player.gun == self.gun:
				player.scene.create_player_gun()
			return Fall(player)

	def update(self, player, dt):
		
		player.acc.x = 0
		player.input()
		player.physics_x(dt)
		player.physics_y(dt)

		player.animate('double_jump', 0.25 * dt, False)