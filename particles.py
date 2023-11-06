import pygame
from settings import *

class MuzzleFlash(pygame.sprite.Sprite):
	def __init__(self, game, scene, firer, groups, pos, z, path):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.firer = firer
		self.z = z
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect()

		self.hitbox = self.rect.copy().inflate(0,0)
		self.alive = True

	def animate(self, animation_speed, loop=True):

		self.frame_index += animation_speed

		if loop:
			self.frame_index = self.frame_index % len(self.frames)	
		else:
			if self.frame_index > len(self.frames)-1:	
				# self.frame_index = len(self.frames)-1
				self.kill()

		self.image = self.frames[int(self.frame_index)]

	def update(self, dt):
		self.animate(0.2 * dt, False)

		self.rect.center = self.firer.muzzle_pos + self.scene.drawn_sprites.offset

class BlasterParticle(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.z = z

		self.image = pygame.Surface((2,2))
		self.image.fill(YELLOW)
		self.rect = self.image.get_rect(center = pos)

		self.alpha = 255

	def update(self, dt):

		self.alpha -= 15 * dt
		if self.alpha < 0:
			self.kill()

		self.image.set_alpha(self.alpha)