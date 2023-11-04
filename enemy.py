import pygame
from settings import *
from enemy_fsm import Fall

class Guard(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, name, z):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.name = name
		self.z = z
		self.state = Fall(self)
		self.animations = {'idle':[], 'run':[], 'land':[], 'jump':[], 'fall':[]}
		self.import_images(self.animations)
		self.frame_index = 0
		self.image = self.animations['fall'][self.frame_index].convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.old_pos = self.pos.copy()
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)
		self.old_hitbox = self.hitbox.copy()

		self.gravity = 0.15
		self.acc_rate = 0.6
		self.fric = -0.2
		self.acc = pygame.math.Vector2(0, self.gravity)	
		self.vel = pygame.math.Vector2()
		self.max_fall_speed = 6
		self.jump_height = 4
		self.facing = 1


		self.platform = None
		self.relative_position = pygame.math.Vector2()
		self.on_ground = False
		self.drop_through = False

		self.gun = DATA['enemy_guns'][self.name]
		self.muzzle_pos = None
		self.vision_box = pygame.Rect(0, 0, 300, 200)

	def import_images(self, animation_states):

		path = f'assets/characters/{self.name}/'

		for animation in animation_states.keys():
			full_path = path + animation
			animation_states[animation] = self.game.get_folder_images(full_path)

	def animate(self, state, speed, loop=True):

		self.frame_index += speed

		if self.frame_index >= len(self.animations[state]):
			if loop: 
				self.frame_index = 0
			else:
				self.frame_index = len(self.animations[state]) -1
		
		self.image = pygame.transform.flip(self.animations[state][int(self.frame_index)], self.facing, False)
		
	def jump(self, height):
		self.vel.y = -height

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
			if self.hitbox.colliderect(sprite.raycast_box): 
				if self.old_hitbox.bottom <= sprite.hitbox.top + 4 and self.hitbox.bottom + 4 >= sprite.hitbox.top:
					if self.vel.y >= 0 and not self.drop_through:
						self.hitbox.bottom = sprite.rect.top
						self.on_ground = True
						self.vel.y = 0

						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

						self.platform = sprite
						self.relative_position = self.pos - self.platform.pos
				else:
					self.drop_through = False

	def lerp(self, v0, v1, t):
		return v0 + t * (v1 - v0)

	def get_equidistant_points(self, point_1, point_2, num_of_points):
		return [(self.lerp(point_1[0], point_2[0], 1./num_of_points * i), self.lerp(point_1[1], point_2[1], 1./num_of_points * i)) for i in range(num_of_points + 1)]

	def get_distance(self, point_1, point_2):
		distance = (pygame.math.Vector2(point_2) - pygame.math.Vector2(point_1))
		return distance


	def has_los(self):
		x = self.scene.player.rect.center - self.scene.drawn_sprites.offset
		y = self.rect.center - self.scene.drawn_sprites.offset - pygame.math.Vector2(0, 5)
		distance = int(self.get_distance(y, x).magnitude()//5)
		if distance != 0 and distance < 100:
			for point in self.get_equidistant_points(y, x, distance):
				for sprite in self.scene.block_sprites:
					if sprite.rect.collidepoint(point + self.scene.drawn_sprites.offset):
						return False
		return True

	def physics_x(self, dt):
			
		self.acc.x += self.vel.x * self.fric
		self.vel.x += self.acc.x * dt

		if self.platform and self.platform.vel.x != 0:
			self.pos.x = round(self.platform.pos.x) +round(self.relative_position.x)

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
			self.platform = None

	# def update(self, dt):
		
	# 	self.old_pos = self.pos.copy()
	# 	self.old_hitbox = self.hitbox.copy()

	# 	self.vision_box.center = self.rect.center

	# 	self.acc.x = 0
	# 	self.physics_x(dt)
	# 	self.physics_y(dt)

	def state_logic(self):
		new_state = self.state.state_logic(self)
		if new_state: self.state = new_state
		else: self.state

	def update(self, dt):

		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()
		self.vision_box.center = self.rect.center

		self.state_logic()
		self.state.update(self, dt)
		
		
		





