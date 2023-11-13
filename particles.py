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
		self.rect = self.image.get_rect(center = self.firer.muzzle_pos + self.scene.drawn_sprites.offset)

		self.alpha = 255

	def animate(self, animation_speed, loop=True):

		self.frame_index += animation_speed

		if loop:
			self.frame_index = self.frame_index % len(self.frames)	
		else:
			if self.frame_index > len(self.frames)-1:	
				# self.frame_index = len(self.frames)-1
				self.kill()

		self.image = self.frames[int(self.frame_index)]

	def update_alpha(self, rate, dt):
		self.alpha -= rate * dt
		if self.alpha < 0:
			self.kill()
		self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.animate(0.2 * dt, False)
		self.update_alpha(20, dt)
		self.rect.center = self.firer.muzzle_pos + self.scene.drawn_sprites.offset


class FadeParticle(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z, colour=(255,255,255)):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.z = z
		self.image = pygame.Surface((2,2))
		self.image.fill(colour)
		self.rect = self.image.get_rect(center = pos)

		self.alpha = 255

	def update_alpha(self, rate, dt):
		self.alpha -= rate * dt
		if self.alpha < 0:
			self.kill()
		self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.update_alpha(20, dt)

class ShotgunParticle(FadeParticle):
	def __init__(self, game, scene, groups, pos, z):
		super().__init__(game, scene, groups, pos, z)

		self.image = pygame.image.load('assets/particles/shotgun.png').convert_alpha()
		self.rect = self.image.get_rect(center = pos)

	def update_alpha(self, rate, dt):
		self.alpha -= rate * dt
		if self.alpha < 0:
			self.kill()
		self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.update_alpha(15, dt)

class RocketParticle(FadeParticle):
	def __init__(self, game, scene, groups, pos, z):
		super().__init__(game, scene, groups, pos, z)

		self.image = pygame.Surface((8,8))
		self.image.fill(WHITE)
		self.rect = self.image.get_rect(center = pos)

	def update_alpha(self, rate, dt):
		self.alpha -= rate * dt
		if self.alpha < 0:
			self.kill()
		self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.update_alpha(15, dt)

class RailParticle(FadeParticle):
	def __init__(self, game, scene, groups, pos, z, num, angle):
		super().__init__(game, scene, groups, pos, z)

		self.num = num
		self.angle = angle

		self.alpha = self.get_initial_alpha(24)

		self.image = self.get_flipped_image(pygame.image.load('assets/particles/railgun.png').convert_alpha())
		self.rect = self.image.get_rect(center = pos)
		
	def get_initial_alpha(self, rate):
		alpha = self.num/rate * 255
		return alpha

	def get_flipped_image(self, image):

		if self.angle < 180:
			image = pygame.transform.rotate(pygame.transform.flip(image, True, False), self.angle)	
		else:
			image = pygame.transform.rotate(image, self.angle)

		return image
			
	def update(self, dt):
		self.update_alpha(3, dt)

		
		