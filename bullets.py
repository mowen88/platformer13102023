import pygame, random
from math import atan2, degrees, pi
from settings import *


class Bullet(pygame.sprite.Sprite):
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
			self.scene.create_blaster_particle(random.choice([self.rect.midtop, self.rect.midbottom]))
			self.timer = 0

	def update(self, dt):
		self.collide()
		#self.animate(0.25 * dt)
		self.pos += self.vel * dt
		self.rect.center = self.pos
		self.particles(dt)

