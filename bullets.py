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

		self.speed = 5
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
		if self.timer > 2:
			self.scene.create_particle(self.firer.gun, random.choice([self.rect.midtop, self.rect.midbottom]))
			self.timer = 0

	def move(self, dt):
		self.pos += self.vel * dt
		self.rect.center = self.pos

	def update(self, dt):
		self.collide()
		#self.animate(0.25 * dt)
		self.move(dt)
		self.particles(dt)

class ShotgunShot(BlasterBullet):
	def __init__(self, game, scene, firer, groups, pos, z, angle):
		super().__init__(game, scene, firer, groups, pos, z)

		self.image = pygame.Surface((2,2))
		self.image.fill((255, 255 ,255))
		self.rect = self.image.get_rect(center = pos)
		self.speed = 12
		self.alpha = 255
		self.vel = self.scene.get_distance_direction_and_angle(self.firer.rect.center, pygame.mouse.get_pos())[1] * self.speed
		self.vel = self.vel.rotate(angle)

	def update_alpha(self, rate, dt):
		self.alpha += rate * dt
		if self.alpha <= 0:
			self.alpha == 0
		self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.collide()
		self.update_alpha(-30, dt)
		self.move(dt)

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


