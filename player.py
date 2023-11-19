import pygame, math
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
		self.import_images(self.animations, SAVE_DATA['armour_type'])

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

		self.gun = list(CONSTANT_DATA['guns'].keys())[SAVE_DATA['gun_index']]
		self.muzzle_pos = None
		self.cooldown = 0
		self.underwater = False
		self.max_underwater_time = 300
		self.underwater_timer = self.max_underwater_time

		self.state = Fall(self)

	def import_images(self, animation_states, armour_type):

		if armour_type is not None:
			path = f'assets/characters/{self.name + "_" + armour_type}/'
		else:
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

	def collect(self):
		for sprite in self.scene.pickup_sprites:
			if self.hitbox.colliderect(sprite.hitbox):

				self.scene.create_particle('flash', sprite.hitbox.center)

				if sprite.name in list(CONSTANT_DATA['guns'].keys()):
				
					if sprite.name not in SAVE_DATA['guns_collected']:
						SAVE_DATA['guns_collected'].append(sprite.name)

					sprite.kill()
					self.change_weapon(1, sprite.name)
					ammo_type = CONSTANT_DATA['guns'][sprite.name]['ammo_type']
					ammo_added = CONSTANT_DATA['guns'][sprite.name]['ammo_given']
					capacity_type = SAVE_DATA['ammo_capacity']
					max_ammo = AMMO_LIMITS[capacity_type][ammo_type]

					AMMO_DATA[ammo_type] = min(AMMO_DATA[ammo_type] + ammo_added, max_ammo)
					SAVE_DATA.update({'ammo':AMMO_DATA[ammo_type]})


				elif sprite.name in list(AMMO_DATA.keys()):
					sprite.kill()
					ammo_type = sprite.name
					# get list of guns that use this ammo tye
					guns = self.get_gun_from_ammo_type(ammo_type)
					# get 1 gun from the above list to use in getting

					# using guns[0], any gun in guns list to get the relevant gun for ammo given
					ammo_added = CONSTANT_DATA['guns'][guns[0]]['ammo_given']
					capacity_type = SAVE_DATA['ammo_capacity']
					max_ammo = AMMO_LIMITS[capacity_type][ammo_type]
					
					AMMO_DATA[ammo_type] = min(AMMO_DATA[ammo_type] + ammo_added, max_ammo)

					#if current gun is same ammo type, update SAVE_DATA['ammo']
					if self.gun in guns:
						SAVE_DATA.update({'ammo':AMMO_DATA[ammo_type]})	

				elif sprite.name == 'jacket':
					sprite.kill()
					SAVE_DATA.update({'armour_type':sprite.name})
					self.import_images(self.animations, SAVE_DATA['armour_type'])

				else:
					sprite.kill()
					
	def get_gun_from_ammo_type(self, ammo_type):
		guns = []
		for gun, attributes in CONSTANT_DATA['guns'].items():
			if 'ammo_type' in attributes and attributes['ammo_type'] == ammo_type:
				guns.append(gun)
		return guns

	def change_weapon(self, direction, gun_collected=None):	

		if len(SAVE_DATA['guns_collected']) > 1:
			self.gun_sprite.kill()
		
			num_of_guns = len(list(CONSTANT_DATA['guns'].keys()))
		
			while True:
				SAVE_DATA['gun_index'] += direction

				if SAVE_DATA['gun_index'] >= num_of_guns:
					SAVE_DATA['gun_index'] = 0
				elif SAVE_DATA['gun_index'] < 0:
					SAVE_DATA['gun_index'] = num_of_guns-1

				current_gun = list(CONSTANT_DATA['guns'].keys())[SAVE_DATA['gun_index']]

				if gun_collected is not None:
					if current_gun == gun_collected:
						break

				elif current_gun in SAVE_DATA['guns_collected']:
					break	
			
			self.gun = current_gun
			SAVE_DATA.update({'ammo':AMMO_DATA[CONSTANT_DATA['guns'][self.gun]['ammo_type']]})

			self.scene.create_player_gun()
			self.cooldown = 0

	def exit_scene(self):
		for door in self.scene.exit_sprites:
			if self.hitbox.colliderect(door.rect) and ACTIONS['up']:
				self.scene.exiting = True
				self.scene.new_scene = SCENE_DATA[self.scene.scene_num][door.name]
				self.scene.entry_point = door.name

	def hit_liquid(self, dt):
	    for sprite in self.scene.liquid_sprites:
	        if self.hitbox.colliderect(sprite.hitbox):
	            if not self.underwater:
	                self.underwater = True
	                if self.old_hitbox.bottom <= sprite.hitbox.top <= self.hitbox.bottom:
	                    self.scene.create_particle('splash', (self.hitbox.centerx, sprite.hitbox.centery - TILESIZE))
	        elif self.underwater and self.old_hitbox.bottom >= sprite.hitbox.top >= self.hitbox.bottom:
	            self.scene.create_particle('splash', (self.hitbox.centerx, sprite.hitbox.centery - TILESIZE))
	            self.underwater = False

	    # breathing / drowning logic
	    if self.underwater:
	    	self.underwater_timer -= dt
	    else:
	    	self.underwater_timer = self.max_underwater_time

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

	def got_headroom(self):
		for sprite in self.scene.block_sprites:
			if sprite.hitbox.collidepoint((self.hitbox.centerx, self.hitbox.y - 8)):
				return True
		return False

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
				CONSTANT_DATA['guns']['chain gun']['cooldown'] -= 0.05 * dt
			else:
				CONSTANT_DATA['guns']['chain gun']['cooldown'] += 0.1 * dt

		CONSTANT_DATA['guns']['chain gun']['cooldown'] = max(2, min(CONSTANT_DATA['guns']['chain gun']['cooldown'], 10))

		return CONSTANT_DATA['guns']['chain gun']['cooldown']

	def fire(self):
		if self.gun_sprite in self.scene.gun_sprites and self.cooldown <= 0\
		 and CONSTANT_DATA['guns'][self.gun]['ammo_used'] <= SAVE_DATA['ammo'] and self.scene.fade_surf.alpha == 0: #and SAVE_DATA['ammo'] > 0:
			if not self.scene.exiting:
				self.scene.create_bullet(self, CONSTANT_DATA['guns'][self.gun]['auto'])
				self.cooldown = CONSTANT_DATA['guns'][self.gun]['cooldown']

	def hit_by_bullet(self):
		for sprite in self.scene.bullet_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				ammo_type = CONSTANT_DATA['guns'][sprite.firer.gun]['ammo_type']
				self.reduce_health(sprite.damage, ammo_type)
				sprite.kill()

	def reduce_health(self, amount, ammo_type):
		armour_coefficients = {None:[0.0, 0.0], 'jacket': [0.3, 0.0], 'combat':[0.6,0.3], 'body':[0.8,0.6]}
		# determine energy weapon or normal for armour damage coefficient
		coefficient = armour_coefficients[SAVE_DATA['armour_type']][0] if ammo_type not in ['blaster', 'cells'] else armour_coefficients[SAVE_DATA['armour_type']][1]
		armour_reduction = min(amount * coefficient, SAVE_DATA['armour'])
		health_reduction = amount - armour_reduction

		SAVE_DATA['armour'] -= armour_reduction
		if SAVE_DATA['armour'] < 0:
			SAVE_DATA['health'] += SAVE_DATA['armour']
			SAVE_DATA['armour'] = 0

		SAVE_DATA['health'] -= health_reduction
		SAVE_DATA['health'] = max(0, SAVE_DATA['health'])

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
		self.collect()
		self.hit_liquid(dt)
		


	


		
		
		





