import pygame
from settings import *

class Explosion(pygame.sprite.Sprite):
	def __init__(self, game, groups, pos, z, path, damage=0, knockback_power=0):
		super().__init__(groups)
		self.game = game
		self.z = z
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

		self.damage = damage
		self.knockback_power = knockback_power

	def animate(self, animation_speed):

		self.frame_index += animation_speed
		self.frame_index = self.frame_index % len(self.frames)	
		self.image = self.frames[int(self.frame_index)]
		if self.frame_index > len(self.frames)-1:	
			self.kill()

	def update(self, dt):
		self.animate(0.2 * dt)

class DustParticle(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z, path):
		super().__init__(groups)
		self.game = game
		self.scene = scene
		self.z = z
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)
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
		self.animate(0.25 * dt, False)
		self.update_alpha(10, dt)

class MuzzleFlash(DustParticle):
	def __init__(self, game, scene, groups, pos, z, path, firer):
		super().__init__(game, scene, groups, pos, z, path)

		self.firer = firer
		self.rect = self.image.get_rect(center = self.firer.muzzle_pos + self.scene.drawn_sprites.offset)

	def update(self, dt):
		self.animate(0.2 * dt, False)
		self.update_alpha(20, dt)
		self.rect.center = self.firer.muzzle_pos + self.scene.drawn_sprites.offset

class FadeParticle(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z, surf=None, colour=((WHITE))):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.z = z
		self.surf = surf
		self.colour = colour
		
		self.image = self.get_image()

		self.rect = self.image.get_rect(center = pos)

		self.alpha = 255

	def get_image(self):
		if self.surf == None:
			image = pygame.Surface((2,2))
			image.fill(self.colour)
		else:
			image = self.surf
		return image

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
		self.update_alpha(2, dt)


class Flash(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, colour, size, z = LAYERS['foreground']):
		super().__init__(groups)

		self.scene = scene
		self.colour = colour
		self.size = size
		self.z = z
		self.pos = pos
		self.alpha = 255
		self.flash_size = [0,0]
		self.image = pygame.Surface((self.flash_size))
		self.image.fill(self.colour)
		self.rect = self.image.get_rect(center = self.pos)

	def update(self, dt):
		
		self.image.fill(self.colour)
		self.alpha -= 12 * dt
		self.flash_size[0] += self.size * dt
		self.flash_size[1] += self.size * dt

		if self.alpha < 0:
			self.kill()

		self.image = pygame.transform.scale(self.image, (self.flash_size))
		self.image.set_alpha(self.alpha)
		self.rect = self.image.get_rect(center = self.pos)