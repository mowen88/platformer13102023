import pygame
from settings import *
from player_fsm import Fall

class Player(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, name, z):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.name = name
		self.z = z
		
		self.animations = {'crouch':[], 'idle':[], 'run':[], 'land':[], 'jump':[], 'double_jump':[], 'fall':[], 'skid':[], 'on_ladder_idle':[], 'on_ladder_move':[]}
		self.import_images(self.animations)
		self.frame_index = 0
		self.image = self.animations['fall'][self.frame_index].convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.old_pos = self.pos.copy()
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)
		self.old_hitbox = self.hitbox.copy()

		self.gravity = 0.15
		self.acc_rate = 0.4
		self.fric = -0.15
		self.acc = pygame.math.Vector2(0, self.gravity)	
		self.vel = pygame.math.Vector2()
		self.max_fall_speed = 6
		self.jump_height = 3.5
		self.facing = 1

		self.on_ladder = False
		self.platform = None
		self.relative_position = pygame.math.Vector2()
		self.on_ground = False
		self.drop_through = False

		self.jump_counter = 0
		self.cyote_timer = 0
		self.cyote_timer_threshold = 6
		self.jump_buffer_active = False
		self.jump_buffer = 0
		self.jump_buffer_threshold = 6

		self.gun_index = 5
		self.gun = list(DATA['guns'].keys())[self.gun_index]
		self.muzzle_pos = None
		self.cooldown = 0

		self.health = 100

		self.state = Fall(self)

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

	def get_on_ground(self):
		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox = self.rect.inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)

	def input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
			self.acc.x = -self.acc_rate
			
		elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
			self.acc.x = self.acc_rate

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
					if self.vel.y > 0 and not self.drop_through:
						self.hitbox.bottom = sprite.rect.top
						self.on_ground = True
						self.vel.y = 0

						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

						self.platform = sprite
						self.relative_position = self.pos - self.platform.pos
				else:
					self.drop_through = False

	def collide_ladders(self):
		for sprite in self.scene.ladder_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.centerx > sprite.hitbox.left and self.hitbox.centerx < sprite.hitbox.right:
					return True
		return False

	def physics_x(self, dt):
			
		self.acc.x += self.vel.x * self.fric
		self.vel.x += self.acc.x * dt

		if self.platform and self.platform.vel.x != 0:
			self.pos.x = round(self.platform.pos.x) +round(self.relative_position.x)

		self.pos.x += self.vel.x * dt + (0.5 * self.acc.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collisions_x(self.scene.block_sprites)

		self.collide_platforms(self.scene.platform_sprites, dt)

	def physics_y(self, dt):

		self.vel.y += self.acc.y * dt
		self.pos.y += self.vel.y * dt + (0.5 * self.acc.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		self.collisions_y(self.scene.block_sprites)
	
		if self.vel.y >= self.max_fall_speed: 
			self.vel.y = self.max_fall_speed

		if abs(self.vel.y) >= 0.5: 
			self.on_ground = False
			self.platform = None

	def ladder_physics(self, dt):

		# x direction (multiply friction by 4 so easier to manage x direction on ladders)
		self.acc.x += self.vel.x * self.fric * 4
		self.vel.x += self.acc.x * dt
		self.pos.x += self.vel.x * dt + (0.5 * self.vel.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collisions_x(self.scene.block_sprites)
		
		#y direction
		self.acc.y += self.vel.y * self.fric * 2
		self.vel.y += self.acc.y * dt
		self.pos.y += self.vel.y * dt + (0.5 * self.vel.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		self.collisions_y(self.scene.block_sprites)

	def handle_jumping(self, dt):
		# Double the gravity if not holding jump key to allow variale jump height
		if not pygame.mouse.get_pressed()[2] and self.vel.y < 0:
			self.acc.y = self.gravity * 2.5
		else:
			self.acc.y = self.gravity

		# incrememnt cyote timer when not on ground
		if not self.on_ground: 
			self.cyote_timer += dt
		else: 
			self.cyote_timer = 0

		# # if falling, this gives the player one jump if they have double jump
		# if self.jump_counter == 0 and self.cyote_timer < self.cyote_timer_threshold:
		# 	self.jump_counter = 1

		# jump buffer activated if pressing jump in air
		if self.jump_buffer_active:
			self.jump_buffer += dt
			if self.jump_buffer >= self.jump_buffer_threshold:
				self.jump_buffer = 0
				self.jump_buffer_active = False

	def cooldown_timer(self, dt):
		if self.cooldown > 0:
			self.cooldown -= dt

	def chain_gun_spin_up(self, dt):
		if self.gun == 'chain gun':
			if ACTIONS['left_click']:
				DATA['guns']['chain gun']['cooldown'] -= 0.05 * dt
			else:
				DATA['guns']['chain gun']['cooldown'] += 0.1 * dt

		DATA['guns']['chain gun']['cooldown'] = max(2, min(DATA['guns']['chain gun']['cooldown'], 10))

		return DATA['guns']['chain gun']['cooldown']

	def hit_by_bullet(self):
		for sprite in self.scene.bullet_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				self.reduce_health(sprite.damage)
				sprite.kill()

	def reduce_health(self, amount):
		# if not self.invincible:
		self.health -= amount
		if self.health <= 0:
			pass#self.alive = False
			# set new zone to the current one to re-enter after death
			#self.zone.new_zone = self.zone.name
			# self.zone.create_zone(self.zone.name)

	def state_logic(self):
		new_state = self.state.state_logic(self)
		if new_state: self.state = new_state
		else: self.state

	def update(self, dt):

		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()

		self.state_logic()
		self.state.update(self, dt)
		self.handle_jumping(dt)
		self.cooldown_timer(dt)
		self.chain_gun_spin_up(dt)
		self.hit_by_bullet()


	


		
		
		





