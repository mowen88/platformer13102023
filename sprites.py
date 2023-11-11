import pygame, math
from settings import *

class Collider(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE))):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(2,0)

class Tile(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE)), z= LAYERS['blocks']):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z, path, animation_type=None):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.z = z
		self.animation_type = animation_type
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

		self.hitbox = self.rect.copy().inflate(0,0)
		self.alive = True

	def animate(self, animation_speed):

		self.frame_index += animation_speed

		if self.animation_type == 'loop':
			self.frame_index = self.frame_index % len(self.frames)

		elif self.animation_type == 'end':
			if self.frame_index > len(self.frames)-1:
				self.frame_index = len(self.frames)-1
		else:
			if self.frame_index > len(self.frames)-1:
				self.kill()

		self.image = self.frames[int(self.frame_index)]

	def update(self, dt):
		self.animate(0.2 * dt)


class MovingPlatform(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf, z, direction, amplitude, circular=None):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)	
		self.z = z
		self.circular = circular
		self.hitbox = self.rect.copy()
		self.raycast_box = self.hitbox.copy().inflate(0,2)
		self.old_hitbox = self.hitbox.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		
		self.direction = pygame.math.Vector2(direction)
		self.vel = pygame.math.Vector2()
		self.start_pos = pygame.math.Vector2(self.rect.center)
		self.amplitude = amplitude

	def move(self, dt):
		# Update the position using a sine wave pattern
		self.vel += self.direction * dt

		self.pos.x = self.start_pos.x + self.amplitude * math.sin(self.vel.x)

		if self.circular:
			self.pos.y = self.start_pos.y + self.amplitude * math.cos(self.vel.y)
		else:
			self.pos.y = self.start_pos.y + self.amplitude * math.sin(self.vel.y)

		self.hitbox.centerx = round(self.pos.x)
		self.hitbox.centery = round(self.pos.y)
		self.rect.center = self.hitbox.center
		self.raycast_box.midbottom = self.hitbox.midtop


	def update(self, dt):
		#get pos before it is updated to get the displacement of movement per frame and pass it to the player platform_speed
		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()
		self.move(dt)
		

		

