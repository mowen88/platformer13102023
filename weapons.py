import pygame
from math import atan2, degrees, pi
from settings import *

class Gun(pygame.sprite.Sprite):
	def __init__(self, game, scene, gun_type, owner, groups, pos, z):
		super().__init__(groups)

		self.scene = scene
		self.gun_type = gun_type
		self.owner = owner
		self.z = z
		
		self.original_image = pygame.image.load(f'assets/guns/gun1.png').convert_alpha()
		self.image = self.original_image
		self.flipped_image = pygame.transform.flip(self.original_image, True, False)
		self.rect = self.image.get_rect(center = pos)
		self.angle = 0
		self.total_angles = 90

		self.image_cache = self.get_image_cache()

	def get_angle(self, point_1, point_2):
		dx = point_1[0] - point_2[0] - self.scene.drawn_sprites.offset[0]
		dy = point_1[1] - point_2[1] - self.scene.drawn_sprites.offset[1]
		radians = atan2(dx, dy)
		radians %= 2 * pi
		self.angle = int(degrees(radians))

	def get_image_cache(self):
		image_cache = []
		for angle in range(self.total_angles):
			rotated_image = pygame.transform.rotate(self.image, angle * 360 / self.total_angles)
			image_cache.append(rotated_image)
		return image_cache

	def rotate(self):
		if self.angle >= 180: 
			self.image = self.image_cache[int(self.total_angles * (self.angle % 360) /360)]
		else: 
			self.image = pygame.transform.rotate(self.original_image, self.angle)

		self.rect = self.image.get_rect(center = self.rect.center)

	def update(self, dt):
		if self.owner != self.scene.player: 
			self.get_angle(self.rect.center + self.scene.drawn_sprites.offset, self.scene.player.hitbox.center)
		else: 
			self.get_angle(self.rect.center, pygame.mouse.get_pos())
		self.rotate()
		self.rect.center = (self.owner.hitbox.centerx, self.owner.hitbox.centery - 4)