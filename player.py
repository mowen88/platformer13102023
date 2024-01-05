import pygame, math, random
from settings import *
from message import Message
from player_fsm import Hold


class Player(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, name, z):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.name = name
		self.z = z
		
		self.animations = {'normal':{'death':[], 'crouch':[], 'idle':[], 'run':[], 'land':[], 'jump':[], 'double_jump':[], 'fall':[], 'skid':[], 'on_ladder_idle':[], 'on_ladder_move':[]},
		'jacket':{'death':[], 'crouch':[], 'idle':[], 'run':[], 'land':[], 'jump':[], 'double_jump':[], 'fall':[], 'skid':[], 'on_ladder_idle':[], 'on_ladder_move':[]},
		'combat':{'death':[], 'crouch':[], 'idle':[], 'run':[], 'land':[], 'jump':[], 'double_jump':[], 'fall':[], 'skid':[], 'on_ladder_idle':[], 'on_ladder_move':[]},
		'body':{'death':[], 'crouch':[], 'idle':[], 'run':[], 'land':[], 'jump':[], 'double_jump':[], 'fall':[], 'skid':[], 'on_ladder_idle':[], 'on_ladder_move':[]}
		}
		self.import_images(SAVE_DATA['armour_type'])

		self.frame_index = 0
		self.image = self.animations[SAVE_DATA['armour_type']]['fall'][self.frame_index].convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.old_pos = self.pos.copy()
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5,- self.rect.height * 0.5)
		self.old_hitbox = self.hitbox.copy()

		self.gravity = 0.15
		self.acc_rate = 0.4
		self.fric = -0.2
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
		self.drown_damage = 4
		self.hazardous_liquid_timer = 0
		self.hazardous_liquid_hurt_interval = 600
		self.in_hazardous_liquid = False
		self.hazardous_liquid_type = None

		self.quad_damage = False
		self.invulnerable = False
		self.rebreather = False
		self.envirosuit = False
		self.hurt = False
		self.alive = True
		self.state = Hold(self)

	def import_images(self, armour_type):

		for armour_type in self.animations.keys():

			path = f'assets/characters/{self.name + "_" + armour_type}/'
			
			for animation in self.animations[armour_type].keys():
				full_path = path + animation
				self.animations[armour_type][animation] = self.game.get_folder_images(full_path)

	def animate(self, state, speed, loop=True):

		self.frame_index += speed

		if self.frame_index >= len(self.animations[SAVE_DATA['armour_type']][state]):
			if loop: 
				self.frame_index = 0
			else:
				self.frame_index = len(self.animations[SAVE_DATA['armour_type']][state]) -1
		
		self.image = pygame.transform.flip(self.animations[SAVE_DATA['armour_type']][state][int(self.frame_index)], self.facing, False)

	def jump(self, height):
		self.vel.y = -height
		self.game.world_fx['jump'].play()

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
				#SAVE_DATA['killed_sprites'].append(sprite.name)
				name = sprite.name.split('_')[0]
				# show message on screen
				# message = f'{sprite.name.split('_')[0]} armour' if sprite.name.split('_')[0] in list(ARMOUR_DATA.keys()) else sprite.name.split('_')[0]

				if name == 'shard':
					message = f'armour {name}'
				elif name in list(ARMOUR_DATA.keys()):
					message = f'{name} armour'
				else:
					message = name
	
				if name in list(CONSTANT_DATA['guns'].keys()):

					self.game.item_fx['shard'].play()
				
					ammo_type = CONSTANT_DATA['guns'][name]['ammo_type']
					ammo_added = CONSTANT_DATA['guns'][name]['ammo_given']
					capacity_type = SAVE_DATA['ammo_capacity']
					max_ammo = AMMO_LIMITS[capacity_type][ammo_type]

					if AMMO_DATA[ammo_type] < max_ammo:
						sprite.kill()
						if name not in SAVE_DATA['guns_collected']:
							SAVE_DATA['guns_collected'].append(name)
						self.change_weapon(1, name)

						AMMO_DATA[ammo_type] = min(AMMO_DATA[ammo_type] + ammo_added, max_ammo)
						SAVE_DATA.update({'ammo':AMMO_DATA[ammo_type]})
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
						self.scene.create_particle('flash', sprite.hitbox.center)
						SAVE_DATA['killed_sprites'].append(sprite.name)

					else:
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'max capacity reached', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))


				elif name in list(AMMO_DATA.keys()):
					ammo_type = name
					# get list of guns that use this ammo tye
					guns = self.get_gun_from_ammo_type(ammo_type)
					# get 1 gun from the above list to use in getting

					# using guns[0], any gun in guns list to get the relevant gun for ammo given
					ammo_added = CONSTANT_DATA['guns'][guns[0]]['ammo_given']
					capacity_type = SAVE_DATA['ammo_capacity']
					max_ammo = AMMO_LIMITS[capacity_type][ammo_type]
					
					if AMMO_DATA[ammo_type] < max_ammo:
						self.game.item_fx['shard'].play()
						sprite.kill()
						AMMO_DATA[ammo_type] = min(AMMO_DATA[ammo_type] + ammo_added, max_ammo)

						#if current gun is same ammo type, update SAVE_DATA['ammo']
						if self.gun in guns:
							SAVE_DATA.update({'ammo':AMMO_DATA[ammo_type]})	

						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
						self.scene.create_particle('flash', sprite.hitbox.center)
						SAVE_DATA['killed_sprites'].append(sprite.name)

					else:
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'max capacity reached', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))

				elif name in list(ARMOUR_DATA.keys()):
					self.game.item_fx['shard'].play()
					sprite.kill()
					self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
					self.scene.create_particle('flash', sprite.hitbox.center)
					SAVE_DATA['killed_sprites'].append(sprite.name)

					max_armour = ARMOUR_DATA[name][1]
					max_armour = max(max_armour + SAVE_DATA['shards'], SAVE_DATA['max_armour'])
					
					current_armour = SAVE_DATA['armour']
					armour_increase = ARMOUR_DATA[name][0]

					armour_list = list(ARMOUR_DATA.keys())

					if name != 'shard':
						SAVE_DATA.update({'max_armour':max_armour})
						if armour_list.index(name) >= armour_list.index(SAVE_DATA['armour_type']):
							SAVE_DATA.update({'armour_type':name})
							SAVE_DATA.update({'armour':min(current_armour + armour_increase, max_armour)})

						else:
							SAVE_DATA.update({'armour':min(current_armour + armour_increase, max_armour)})

					elif SAVE_DATA['armour_type'] == None:
						SAVE_DATA.update({'shards':SAVE_DATA['shards'] + armour_increase})
						SAVE_DATA.update({'armour':current_armour + armour_increase})
						SAVE_DATA.update({'armour_type':'jacket'})

						max_armour 

					else:
						SAVE_DATA.update({'shards':SAVE_DATA['shards'] + armour_increase})
						SAVE_DATA.update({'max_armour': SAVE_DATA['max_armour'] + armour_increase})
						SAVE_DATA.update({'armour':current_armour + armour_increase})

				elif name in list(HEALTH_DATA.keys()):

					current_health = SAVE_DATA['health']
					health_added = HEALTH_DATA[name]
					max_health = SAVE_DATA['max_health']
					max_health = max(max_health + SAVE_DATA['stimpacks'], SAVE_DATA['max_health'])

					if name == 'stimpack':
						self.game.item_fx['medkit'].play()
						SAVE_DATA.update({'max_health':max_health + health_added})
						SAVE_DATA.update({'health':current_health + health_added})
						sprite.kill()
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
						self.scene.create_particle('flash', sprite.hitbox.center)
						SAVE_DATA['killed_sprites'].append(sprite.name)

					elif SAVE_DATA['health'] < max_health:
						self.game.item_fx['medkit'].play()
						SAVE_DATA.update({'health':min(max_health, current_health + health_added)})
						sprite.kill()
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
						self.scene.create_particle('flash', sprite.hitbox.center)
						SAVE_DATA['killed_sprites'].append(sprite.name)
					else:
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'max capacity reached', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))

				elif name in CONSTANT_DATA['all_items']: 
					if name not in SAVE_DATA['items']:
						self.game.item_fx['collect'].play()
						SAVE_DATA['items'].append(name)
						sprite.kill()
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], message, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
						self.scene.create_particle('flash', sprite.hitbox.center)
						SAVE_DATA['killed_sprites'].append(sprite.name)
					else:
						self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'max capacity reached', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
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
		for exit in self.scene.exit_sprites:
			if self.hitbox.colliderect(exit.hitbox) and ACTIONS['up']:
				self.game.write_game_time()
				self.scene.exiting = True
				self.scene.new_scene = SCENE_DATA[self.scene.current_scene][exit.name.split("_")[0]]
				self.scene.prev_level = SCENE_DATA[self.scene.current_scene]['level']
				self.scene.entry_point = exit.name.split("_")[0]

	def collide_tutorials(self):
		for rect in self.scene.tutorial_sprites:
			if self.hitbox.colliderect(rect.rect) and rect not in SAVE_DATA['killed_sprites']:
				self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], rect.text, (HALF_WIDTH, HEIGHT - TILESIZE * 1.5), 200, NEON_GREEN)
				SAVE_DATA['killed_sprites'].append(rect.text)
				rect.kill()

	def hit_liquid(self, dt):

		#in / out water logic
	    for sprite in self.scene.liquid_sprites:
	    	if sprite.hitbox.left <= self.hitbox.centerx <= sprite.hitbox.right:
		    	if self.hitbox.colliderect(sprite.hitbox):
		    		if self.old_hitbox.bottom <= sprite.hitbox.top <= self.hitbox.bottom:
		    			if 'top' in sprite.name:
		    				self.game.world_fx['splash'].play()
		    				self.scene.create_particle('splash', (self.hitbox.centerx, sprite.hitbox.centery - TILESIZE))

		    	elif self.old_hitbox.bottom >= sprite.hitbox.top >= self.hitbox.bottom:
		        	if 'top' in sprite.name:
		        		self.game.world_fx['splash'].play()
		        		self.scene.create_particle('splash', (self.hitbox.centerx, sprite.hitbox.centery - TILESIZE))
		        		self.in_hazardous_liquid = False

	    	if 'water' in sprite.name:
		        if self.hitbox.colliderect(sprite.hitbox) and 'top' not in sprite.name:
		            if not self.underwater:
		                self.underwater = True
		                self.scene.breathe_timer.start()
		       
		        elif self.old_hitbox.bottom >= sprite.hitbox.top >= self.hitbox.bottom: 
	        		self.underwater = False

	    	elif 'slime' in sprite.name or 'lava' in sprite.name:
	        	if self.hitbox.colliderect(sprite.hitbox):
		            if not self.in_hazardous_liquid:
		                self.in_hazardous_liquid = True
		                self.hazardous_liquid_type = sprite.name

	        	if self.in_hazardous_liquid:
	        		damage = CONSTANT_DATA['liquid_damage'][self.hazardous_liquid_type.split("_")[0]]

	        		if self.hazardous_liquid_timer == 0 and self.old_hitbox.bottom <= sprite.hitbox.top <= self.hitbox.bottom:
	        			if self.scene.envirosuit_timer.running:
	        				damage -= 15
        				if damage > 0:
        					self.reduce_health(damage)

	        		self.hazardous_liquid_timer += dt

	        		if self.hazardous_liquid_timer >= self.hazardous_liquid_hurt_interval:
	        			if self.scene.envirosuit_timer.running:
	        				damage -= 15
        				if damage > 0:
        					self.reduce_health(damage)

        				self.hazardous_liquid_timer = 0
	        	else:
	        		self.hazardous_liquid_timer = 0
	        		self.hazardous_liquid_type = None


	    if self.underwater and not self.scene.rebreather_timer.running and not self.scene.envirosuit_timer.running:
	    	if self.scene.breathe_timer.timer == self.scene.breathe_timer.duration:
	    		self.reduce_health(self.drown_damage)
	    		self.game.world_fx[random.choice(['drowning_0','drowning_1'])].play()
	    		self.drown_damage += 2
	    else:
	    	self.scene.breathe_timer.stop()
	    	self.drown_damage = 4
	
	def get_collidable_sprites(self):
		collidable_list = pygame.sprite.spritecollide(self, self.scene.block_sprites, False)
		return collidable_list

	def collisions_x(self):
		for sprite in self.get_collidable_sprites():
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.right >= sprite.hitbox.left and self.old_hitbox.right <= sprite.old_hitbox.left:
					self.hitbox.right = sprite.hitbox.left
					self.vel.x = 0
				elif self.hitbox.left <= sprite.hitbox.right and self.old_hitbox.left >= sprite.old_hitbox.right:
					self.hitbox.left = sprite.hitbox.right
					self.vel.x = 0

				self.rect.centerx = self.hitbox.centerx
				self.pos.x = self.hitbox.centerx

	def collisions_y(self):
		for sprite in self.get_collidable_sprites():
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
				self.platform = None

	def collide_platforms(self, group, dt):

		for sprite in group:
			if self.hitbox.colliderect(sprite.raycast_box): 
				if self.old_hitbox.bottom <= sprite.hitbox.top + 4 and self.hitbox.bottom >= sprite.hitbox.top -4:
					if self.vel.y >= 0 and not self.drop_through:
						self.hitbox.bottom = sprite.hitbox.top
						self.on_ground = True
						self.vel.y = 0

						self.rect.centery = self.hitbox.centery
						self.pos.y = self.hitbox.centery

						self.platform = sprite

						self.relative_position = self.pos - self.platform.pos


	def collide_ladders(self):
		for sprite in self.scene.ladder_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				if self.hitbox.centerx > sprite.hitbox.left and self.hitbox.centerx < sprite.hitbox.right:
					return True
		return False

	def physics_x(self, dt):
			
		self.acc.x += self.vel.x * self.fric
		self.vel.x += self.acc.x * dt

		if self.platform: 
			if self.hitbox.right < self.platform.hitbox.left or self.hitbox.left > self.platform.hitbox.right:
				self.platform = None
			elif self.platform.vel.x != 0:
				self.pos.x = round(self.platform.pos.x) +round(self.relative_position.x)

		self.pos.x += self.vel.x * dt + (0.5 * self.acc.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collisions_x()


	def physics_y(self, dt):

		self.vel.y += self.acc.y * dt

		if self.platform:
			self.pos.y = round(self.platform.pos.y) +round(self.relative_position.y)

		self.pos.y += self.vel.y * dt + (0.5 * self.acc.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery

		self.collide_platforms(self.scene.platform_sprites, dt)
		self.collisions_y()
	
		if self.vel.y >= self.max_fall_speed: 
			self.vel.y = self.max_fall_speed

		elif abs(self.vel.y) >= 0.5:
			self.on_ground = False
			self.platform = None

	def got_headroom(self):
		for sprite in self.scene.block_sprites:
			raycast_box = pygame.Rect(self.hitbox.x, self.hitbox.y - TILESIZE/2, self.hitbox.width, self.hitbox.height)
			if sprite.hitbox.colliderect(raycast_box):
				return True
		return False

	def ladder_physics(self, dt):

		# x direction (multiply friction by 4 so easier to manage x direction on ladders)
		self.acc.x += self.vel.x * self.fric * 4
		self.vel.x += self.acc.x * dt
		self.pos.x += self.vel.x * dt + (0.5 * self.vel.x) * dt

		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collisions_x()
		
		#y direction
		self.acc.y += self.vel.y * self.fric * 2
		self.vel.y += self.acc.y * dt
		self.pos.y += self.vel.y * dt + (0.5 * self.vel.y) * dt

		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collisions_y()

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

		if CONSTANT_DATA['guns'][self.gun]['ammo_used'] > SAVE_DATA['ammo'] and self.cooldown <= 0:
			self.game.weapon_fx['no_ammo'].play()
			self.cooldown = CONSTANT_DATA['guns']['blaster']['cooldown']

	def hit_by_bullet(self):
		for sprite in self.scene.bullet_sprites:
			if self.hitbox.colliderect(sprite.hitbox):
				ammo_type = CONSTANT_DATA['guns'][sprite.firer.gun]['ammo_type']
				self.reduce_health(sprite.damage, ammo_type)
				self.scene.create_particle('blood', sprite.rect.center)
				sprite.kill()

	def reduce_health(self, amount, ammo_type=False):
		if not self.invulnerable:
			self.hurt = True
			armour_coefficients = {'normal':[0.0, 0.0], 'jacket': [0.3, 0.0], 'combat':[0.6,0.3], 'body':[0.8,0.6]}
			# determine energy weapon or normal for armour damage coefficient
			coefficient = armour_coefficients[SAVE_DATA['armour_type']][0] if ammo_type not in ['blaster', 'cells'] else armour_coefficients[SAVE_DATA['armour_type']][1]
			armour_reduction = min(amount * coefficient, SAVE_DATA['armour'])


			if self.underwater:
				health_reduction = amount
			else:
				if amount < 20:
					self.game.world_fx[random.choice(['pain_0', 'pain_1'])].play()
				else:
					self.game.world_fx[random.choice(['pain_2', 'pain_3'])].play()

				health_reduction = amount - armour_reduction
				SAVE_DATA['armour'] -= armour_reduction
				if SAVE_DATA['armour'] < 0:
					SAVE_DATA['health'] += SAVE_DATA['armour']
					SAVE_DATA['armour'] = 0

			SAVE_DATA['health'] -= health_reduction
			SAVE_DATA['health'] = max(0, SAVE_DATA['health'])

		# if dead
		if SAVE_DATA['health'] <= 0:
			self.alive = False

	def state_logic(self):
		new_state = self.state.state_logic(self)
		if new_state: self.state = new_state
		else: self.state

	def update(self, dt):

		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()

		self.state_logic()
		self.state.update(self, dt)

		if self.alive:
			self.handle_jumping(dt)
			self.cooldown_timer(dt)
			self.chain_gun_spin_up(dt)
			self.hit_by_bullet()
			self.collect()
			self.hit_liquid(dt)
			self.collide_tutorials()
		# self.hit_secret(dt)
		


	


		
		
		





