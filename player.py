import pygame
from settings import *

class Player(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, name, z):
		super().__init__(groups)

		self.scene = scene
		self.name = name
		self.z = z
		self.image = pygame.Surface((16,24))
		self.image.fill(WHITE)
		self.rect = self.image.get_rect(topleft = pos)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.old_pos = self.pos.copy()
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()

		self.gravity = 0.15
		self.acc_rate = 0.5
		self.fric = -0.12
		self.acc = pygame.math.Vector2(0, self.gravity)	
		self.vel = pygame.math.Vector2()
		self.speed = 3
		self.max_fall_speed = 6
		self.parent_platform = None
		self.relative_pos = pygame.math.Vector2()
		self.platform_vel = pygame.math.Vector2()
		self.on_ground = False
		self.on_platform = False

	def jump(self):
		self.vel.y = -4.5

	def input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_LEFT]:
			self.acc.x = -self.acc_rate
			
		elif keys[pygame.K_RIGHT]:
			self.acc.x = self.acc_rate


		if ACTIONS['up']:
			self.jump()
			ACTIONS['up'] = False

	def collisions_x(self, group):
		for sprite in group:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.right >= sprite.hitbox.left and self.old_hitbox.right <= sprite.old_hitbox.left:
					self.hitbox.right = sprite.hitbox.left
					self.vel.x = 0
				elif self.hitbox.left <= sprite.hitbox.right and self.old_hitbox.left >= sprite.old_hitbox.right:
					self.hitbox.left = sprite.hitbox.right
					self.vel.x = 0
				self.rect.centerx = self.hitbox.centerx
				self.pos.x = self.hitbox.centerx

	def collisions_y(self, group):
		for sprite in group:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.bottom >= sprite.hitbox.top and self.old_hitbox.bottom <= sprite.old_hitbox.top:
					self.hitbox.bottom = sprite.hitbox.top
					self.on_ground = True
					self.vel.y = 0

				elif self.hitbox.top <= sprite.hitbox.bottom and self.old_hitbox.top >= sprite.old_hitbox.bottom:
					self.hitbox.top = sprite.hitbox.bottom
					self.vel.y = 0
				self.rect.centery = self.hitbox.centery
				self.pos.y = self.hitbox.centery

	def collide_platforms(self, group, dt):
		for sprite in group:
			platform_raycast = pygame.Rect(sprite.hitbox.x, sprite.hitbox.y - sprite.hitbox.height * 0.2, sprite.hitbox.width, sprite.hitbox.height)
			if self.hitbox.colliderect(sprite.hitbox) or self.hitbox.colliderect(platform_raycast): 
				if self.old_hitbox.bottom <= sprite.hitbox.top + sprite.hitbox.height * 0.2 and self.hitbox.bottom + sprite.hitbox.height * 0.2 >= sprite.hitbox.top and self.vel.y >= 0:

					self.platform_vel = sprite.pos - sprite.old_pos
					self.hitbox.bottom = sprite.rect.top
					self.on_ground = True
					self.vel.y = 0

					self.rect.centery = self.hitbox.centery
					self.pos.y = self.hitbox.centery

					self.parent_platform = sprite
					self.relative_pos = self.pos - self.parent_platform.pos


	def physics_x(self, dt):
			
		print("player: " + str(self.vel.x - self.platform_vel.x))

		

		self.acc.x += self.vel.x * self.fric
		self.vel.x += self.acc.x * dt

		if self.parent_platform and self.on_ground:
			self.pos.x = round(self.parent_platform.pos.x) + round(self.relative_pos.x)

		self.pos.x += self.vel.x * dt + (0.5 * self.acc.x) * (dt*dt)

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collisions_x(self.scene.block_sprites)

		self.collide_platforms(self.scene.platform_sprites, dt)

	def physics_y(self, dt):

		self.vel.y += self.acc.y * dt
		self.pos.y += self.vel.y * dt + (0.5 * self.acc.y) * (dt*dt)

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		self.collisions_y(self.scene.block_sprites)

		if self.vel.y >= self.max_fall_speed: 
			self.vel.y = self.max_fall_speed

		if abs(self.vel.y) >= 0.5: 
			self.on_ground = False

	# 	# limit max fall speed
	# 	if self.vel.y >= self.max_fall_speed: 
	# 		self.vel.y = self.max_fall_speed

	def update(self, dt):
		
		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()

		self.acc.x = 0
		self.input()
		self.physics_x(dt)
		self.physics_y(dt)
		
		
		





