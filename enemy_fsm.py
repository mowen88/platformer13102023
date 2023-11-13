import pygame, random
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
		self.timer = random.randint(50, 200)

	def gun_angle(self, enemy):
		if enemy.facing == 0:
			enemy.gun_sprite.angle = 270
		else:
			enemy.gun_sprite.angle = 90

	def start_stop(self, enemy):
		# when this is called, if enemy is still, it will start moving, otherwise it will stop
		if self.timer <= 0:

			if enemy.facing == 0:
				enemy.move['right'] = True
			else:
				enemy.move['left'] = True

	def state_logic(self, enemy):

		self.start_stop(enemy)

		if not enemy.alive:
			return Death(enemy)

		if not enemy.on_ground:
			return Fall(enemy)

		if enemy.move['left'] or enemy.move['right']:
			return Move(enemy)

		if enemy.player_seen():
			return Telegraph(enemy)

	def update(self, enemy, dt):
		self.gun_angle(enemy)

		self.timer -= dt

		enemy.acc.x = 0
		enemy.move_logic()
		enemy.physics_x(dt)
		enemy.physics_y(dt)
		enemy.animate('idle', 0.25 * dt)

class Move:
	def __init__(self, enemy):
		
		enemy.frame_index = 0
		self.timer = random.randint(50, 80)

	def stop(self, enemy):
		if self.timer <= 0:
			enemy.move.update({key: False for key in enemy.move})

	def state_logic(self, enemy):

		if not enemy.alive:
			return Death(enemy)

		if not enemy.on_ground:
			return Fall(enemy)

		if enemy.player_seen():
			return Telegraph(enemy)

		self.stop(enemy)

		if 0 < enemy.vel.x < 0.1:
			enemy.facing = 0
			return Idle(enemy)
		elif -0.1 < enemy.vel.x < 0:
			enemy.facing = 1
			return Idle(enemy) 

		enemy.turnaround()

	def update(self, enemy, dt):

		self.timer -= dt
	
		enemy.acc.x = 0
		enemy.move_logic()
		
		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('run', 0.25 * dt)

class Telegraph(Move):
	def __init__(self, enemy):
		
		enemy.frame_index = 0
		self.timer = 60
		self.angle = enemy.gun_sprite.get_angle(enemy.rect.center, enemy.scene.player.rect.center)

	def gun_angle(self, enemy):
		if enemy.scene.player.hitbox.colliderect(enemy.vision_box) and enemy.has_los():
			enemy.gun_sprite.get_angle(enemy.rect.center + enemy.scene.drawn_sprites.offset, enemy.scene.player.hitbox.center)

	def state_logic(self, enemy):
		self.stop(enemy)

		if self.timer < 0:
			enemy.scene.create_bullet(enemy, True)
			return Shoot(enemy)

	def update(self, enemy, dt):
		self.gun_angle(enemy)

		self.timer -= dt
	
		enemy.acc.x = 0
		
		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('jump', 0.25 * dt)

class Shoot(Telegraph):
	def __init__(self, enemy):
		
		enemy.frame_index = 0
		self.timer = enemy.data['cooldown']
		

	def state_logic(self, enemy):

		if self.timer < 0:
			if enemy.player_seen():
				return Telegraph(enemy)
			else:
				return Idle(enemy)

	def update(self, enemy, dt):
		self.gun_angle(enemy)

		self.timer -= dt
	
		enemy.acc.x = 0
		
		enemy.physics_x(dt)
		enemy.physics_y(dt)

		enemy.animate('land', 0.25 * dt)

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