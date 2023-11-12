import pygame, random
from math import atan2, degrees, pi
from settings import *


class BlasterBullet(pygame.sprite.Sprite):
	def __init__(self, game, scene, firer, groups, pos, z):
		super().__init__(groups)

		self.scene = scene
		self.firer = firer
		self.z = z
		# self.image = pygame.image.load(f'assets/bullets/{self.firer.gun}/0.png').convert_alpha()
		self.image = pygame.Surface((2,2))
		self.image.fill(YELLOW)
		self.rect = self.image.get_rect(center = pos)

		self.speed = 6
		self.timer = 0
		self.pos = pygame.math.Vector2(self.rect.center)
		self.vel = self.scene.get_distance_direction_and_angle(self.firer.rect.center, pygame.mouse.get_pos())[1] * self.speed
		#self.vel = self.vel.rotate(random.randrange(-10, 10))
		
		# self.damage = GUN_DATA[self.zone.player.gun]['damage']
		# self.knockback_power = GUN_DATA[self.zone.player.gun]['knockback']

	def collide(self):
		for sprite in self.scene.block_sprites:
			if self.rect.colliderect(sprite.hitbox):
				self.kill()

	def particles(self, dt):
		self.timer += dt
		self.scene.create_particle(self.firer.gun, random.choice([self.rect.midtop, self.rect.midbottom]))
		# if self.timer > 2:
		# 	self.scene.create_particle(self.firer.gun, random.choice([self.rect.midtop, self.rect.midbottom]))
		# 	self.timer = 0

	def move(self, dt):
		self.pos += self.vel * dt
		self.rect.center = self.pos

	def update(self, dt):
		self.collide()
		#self.animate(0.25 * dt)
		self.move(dt)
		self.particles(dt)

class Grenade(BlasterBullet):
	def __init__(self, game, scene, firer, groups, pos, z, speed):
		super().__init__(game, scene, firer, groups, pos, z)

		self.gravity = 0.1
		self.speed = speed
		self.vel = self.scene.get_distance_direction_and_angle(self.firer.rect.center, pygame.mouse.get_pos())[1] * self.speed

		self.image = pygame.image.load('assets/particles/grenade.png').convert_alpha()
		self.rect = self.image.get_rect(center = pos)
		self.old_rect = self.rect.copy()

	def collisions_x(self):
		for sprite in self.scene.block_sprites:
			if self.rect.colliderect(sprite.hitbox):
				
				if self.rect.right >= sprite.hitbox.left and self.old_rect.right <= sprite.hitbox.right:
					self.rect.right = sprite.hitbox.left
					self.pos.x = self.rect.x
					self.vel.x *= -1

				if self.rect.left <= sprite.hitbox.right and self.old_rect.left >= sprite.hitbox.right:
					self.rect.left = sprite.hitbox.right
					self.pos.x = self.rect.x
					self.vel.x *= -1

	def collisions_y(self):
		for sprite in self.scene.block_sprites:
			if self.rect.colliderect(sprite.hitbox):
			
				if self.rect.bottom >= sprite.hitbox.top and self.old_rect.bottom <= sprite.hitbox.top:
					self.rect.bottom = sprite.hitbox.top
					self.pos.y = self.rect.y
					self.vel.y *= -0.5
					

				if self.rect.top <= sprite.hitbox.bottom and self.old_rect.top >= sprite.hitbox.bottom:
					self.rect.top = sprite.hitbox.bottom
					self.pos.y = self.rect.y
					self.vel.y *= -2

	def particles(self, dt):
		self.timer += dt
		if self.vel.magnitude() > 1 and self.timer > 4:
			self.scene.create_particle(self.firer.gun, random.choice([self.rect.midtop, self.rect.midbottom]))
			self.timer = 0

	def move(self, dt):
		self.old_rect = self.rect.copy()

		self.pos.x += self.vel.x * dt
		self.rect.centerx = self.pos.x
		self.collisions_x()
		
		self.pos.y += self.vel.y * dt
		self.rect.centery = self.pos.y
		self.collisions_y()

		self.vel.y += self.gravity * dt
		self.vel.x *= 0.99 * dt

		
	def update(self, dt):
		self.move(dt)
		self.particles(dt)
		
class Rocket(BlasterBullet):
	def __init__(self, game, scene, firer, groups, pos, z):
		super().__init__(game, scene, firer, groups, pos, z)

		self.image = pygame.Surface((5,5))
		self.image.fill((255, 0, 0))
		self.rect = self.image.get_rect(center = pos)

	def update(self, dt):
		self.collide()
		#self.animate(0.25 * dt)
		self.move(dt)
		self.particles(dt)


