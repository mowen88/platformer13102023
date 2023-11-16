import pygame, csv, math, random
from math import atan2, degrees, pi
from state import State
from settings import *

from pytmx.util_pygame import load_pygame

from camera import Camera
from player import Player
from enemy import Guard
from sprites import FadeSurf, Collider, Tile, AnimatedTile, MovingPlatform
from weapons import Gun 
from bullets import BlasterBullet, Grenade
from particles import DustParticle, MuzzleFlash, FadeParticle, ShotgunParticle, RocketParticle, RailParticle, Explosion

class Scene(State):
	def __init__(self, game, scene_num, entry_point):
		State.__init__(self, game)


		self.scene_num = scene_num
		self.entry_point = entry_point
		self.scene_size = self.get_scene_size()
		SAVE_DATA.update({'current_scene': self.scene_num, 'entry_pos': self.entry_point})
		# if self.scene_num not in COMPLETED_DATA['visited_zones']:
		# 	COMPLETED_DATA['visited_zones'].append(self.scene_num)

		self.update_sprites = pygame.sprite.Group()
		self.drawn_sprites = Camera(self.game, self)

		self.block_sprites = pygame.sprite.Group()
		self.exit_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		self.ladder_sprites = pygame.sprite.Group()
		
		self.enemy_sprites = pygame.sprite.Group()
		self.gun_sprites = pygame.sprite.Group()
		self.bullet_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		self.railparticle = pygame.sprite.Sprite()

		# fade screen and exit flag
		self.fade_surf = FadeSurf(self.game, self, [self.update_sprites], (0,0))
		self.exiting = False
		
		# create all objects in the scene using tmx data
		self.create_scene_instances()

	def create_scene(self, scene):
		Scene(self.game, scene, self.entry_point).enter_state()

	def get_scene_size(self):
		with open(f'scenes/{self.scene_num}/{self.scene_num}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		return (cols * TILESIZE, rows * TILESIZE)

	def create_scene_instances(self):

		tmx_data = load_pygame(f'scenes/{self.scene_num}/{self.scene_num}.tmx')

		#if 'entries' in self.layers:
		# add the player
		for obj in tmx_data.get_layer_by_name('entries'):
			if obj.name == self.entry_point:
				self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'player', LAYERS['player'])

		for obj in tmx_data.get_layer_by_name('exits'):
				if obj.name == '1': Collider([self.exit_sprites, self.update_sprites, self.collision_sprites], (obj.x, obj.y), obj.name)


		for obj in tmx_data.get_layer_by_name('platforms'):
			if obj.name == '1': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0.02, 0), 80)
			if obj.name == '2': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0, 0.02), 48)
			if obj.name == '3': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0.01, 0), 64)
			if obj.name == '4': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (-0.025, 0.025), 48, 'circular')
			if obj.name == '5': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0, 0.05), 64)
			if obj.name == '6': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0.025, -0.025), 48, 'circular')
			if obj.name == '7': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
				pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0, 0), 16)

		for x, y, surf in tmx_data.get_layer_by_name('blocks').tiles():
			Tile([self.block_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['blocks'])

		for x, y, surf in tmx_data.get_layer_by_name('ladders').tiles():
			Tile([self.ladder_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['blocks'])

		for obj in tmx_data.get_layer_by_name('entities'):
			if obj.name == 'collider': Collider([self.update_sprites, self.collision_sprites], (obj.x, obj.y))
			if obj.name == 'guard': self.guard = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
			if obj.name == 'sg_guard':self.guard2 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
			if obj.name == 'gladiator':self.guard3 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])

		# create gun objects for the enemies and player
		self.create_enemy_guns()
		self.create_player_gun()

	def exit_scene(self):
		for exit in self.exit_sprites:
			if self.player.hitbox.colliderect(exit.rect):
				self.exiting = True
				self.new_scene = SCENE_DATA[self.scene_num][exit.name]
				self.entry_point = exit.name
				return

	def create_player_gun(self):
		self.player.gun_sprite = Gun(self.game, self, self.player, [self.gun_sprites, self.update_sprites, self.drawn_sprites], self.player.hitbox.center, LAYERS['particles'])

	def create_enemy_guns(self):
		for sprite in self.enemy_sprites:
			sprite.gun_sprite = Gun(self.game, self, sprite, [self.gun_sprites, self.update_sprites, self.drawn_sprites], sprite.hitbox.center, LAYERS['particles'])

	def create_bullet(self, sprite, auto=False):

		
		# reset the firing button if the weapon is not an automatic
		if sprite == self.player and not auto:
			ACTIONS['left_click'] = False

		if sprite.gun == 'blaster':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites],sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}',sprite)
			BlasterBullet(self.game, self, sprite, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'])

		elif sprite.gun in ['grenade', 'grenade launcher']:

			speed = 7 if sprite.gun in ['grenade launcher'] else 4
			Grenade(self.game, self, sprite, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], speed)

		elif sprite.gun in ['shotgun', 'super shotgun']:
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			
			lower = -2 # if sprite.gun == 'shotgun' else -4
			upper = 3 # if sprite.gun == 'shotgun' else 6 

			spread_offset = 0.04 if sprite.gun == 'shotgun' else 0.1
			
			for pellet in range(lower, upper):
				pellet *= spread_offset
				self.hitscan(sprite, pellet)

		elif sprite.gun == 'machine gun':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			self.hitscan(sprite, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'chain gun':
			
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			self.hitscan(sprite, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'railgun':
			self.hitscan(sprite)

	def create_particle(self, particle_type, pos):
		if particle_type == 'blaster':
			FadeParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], None, YELLOW)
		elif particle_type == 'landing':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/landing')
		elif particle_type == 'jump':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/jump')
		elif particle_type == 'double_jump':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/double_jump')
		elif particle_type == 'grenade':
			Explosion(self.game, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/explosion')
		else:
			FadeParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], None, LIGHT_GREY)

	# function that returns a list of distance, direciton, angle and dot product from a pair of point coordinates
	# for example, call this aat the index of 0 to return the distance between the player center point and an enemy center point
	def get_distance_direction_and_angle(self, point_1, point_2):
		pos_1 = pygame.math.Vector2(point_1 - self.drawn_sprites.offset)
		pos_2 = pygame.math.Vector2(point_2)
		distance = (pos_2 - pos_1).magnitude()
		
		direction = (pos_2 - pos_1).normalize() if (pos_2 - pos_1).magnitude() != 0 else pygame.math.Vector2(0.1,0.1)

		radians = atan2(-(point_1[0] - (pos_2.x + self.drawn_sprites.offset.x)), (point_1[1] - (pos_2.y + self.drawn_sprites.offset.y)))
		radians %= 2*pi
		angle = int(degrees(radians))

		dot_product_left = pygame.math.Vector2(direction.y, -direction.x).normalize()
		dot_product_right = pygame.math.Vector2(-direction.y, direction.x).normalize()

		return(distance, direction, angle, dot_product_left, dot_product_right)

	def lerp(self, v0, v1, t):
		return v0 + t * (v1 - v0)

	def get_equidistant_points(self, point_1, point_2, num_of_points):
		return [(self.lerp(point_1[0], point_2[0], 1./num_of_points * i), self.lerp(point_1[1], point_2[1], 1./num_of_points * i)) for i in range(num_of_points + 1)]

	def hitscan(self, sprite, offset=0):

		if sprite == self.player:
			gun_damage = DATA['guns'][self.player.gun]['damage']
			angle = math.atan2(pygame.mouse.get_pos()[1]-sprite.gun_sprite.rect.centery + self.drawn_sprites.offset[1],\
					pygame.mouse.get_pos()[0]-sprite.gun_sprite.rect.centerx + self.drawn_sprites.offset[0])
		else:
			gun_damage = DATA['enemies'][sprite.name]['damage']
			angle = math.atan2(self.player.rect.centery-self.drawn_sprites.offset[1]-sprite.gun_sprite.rect.centery + self.drawn_sprites.offset[1],\
					self.player.rect.centerx-self.drawn_sprites.offset[0]-sprite.gun_sprite.rect.centerx + self.drawn_sprites.offset[0])

		x = math.hypot(WIDTH, HEIGHT) * math.cos(angle + offset) + sprite.gun_sprite.rect.centerx
		y = math.hypot(WIDTH, HEIGHT) * math.sin(angle + offset) + sprite.gun_sprite.rect.centery

		distance = ((x, y) - pygame.math.Vector2(sprite.gun_sprite.rect.center)).magnitude()

		
		ammo_type = DATA['guns'][sprite.gun]['ammo_type']

		if sprite.gun in ['shotgun', 'super shotgun', 'machine gun', 'chain gun']:

			point_list = self.get_equidistant_points(sprite.gun_sprite.rect.center, (x, y), int(distance/3))
			for num, point in enumerate(point_list):

				if num > 6:

					# make sure player is clear of its own shot by making sure hte point is far enough away before it can hurt player...
					if self.player.hitbox.collidepoint(point):
						if sprite.gun in ['shotgun', 'super shotgun']:
							gun_damage = round(gun_damage/(num * 0.1))
						self.player.reduce_health(gun_damage, ammo_type)
						if gun_damage > 0:
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
						return True

					for sprite in self.block_sprites:
						if sprite.hitbox.collidepoint(point):
							ShotgunParticle(self.game, self, [self.update_sprites, self.drawn_sprites], point_list[num-1], LAYERS['particles'])
							return True

					for sprite in self.enemy_sprites:
						if sprite.hitbox.collidepoint(point):
							if sprite.gun in ['shotgun', 'super shotgun']:
								gun_damage = round(gun_damage/(num * 0.1))
							sprite.reduce_health(gun_damage, ammo_type)
							if gun_damage > 0:
								AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
							return True

		elif sprite.gun == 'railgun':
			hit_sprites = set()
	
			gun_angle = sprite.gun_sprite.angle
			point_list = self.get_equidistant_points(sprite.gun_sprite.rect.center, (x, y), int(distance/6))
			for num, point in enumerate(point_list):

				if num >= 3 and num <= len(point_list)-2 and num%2==0:
					
					RailParticle(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], num, gun_angle) #pygame.draw.circle(self.game.screen, NEON_BLUE, point - self.drawn_sprites.offset, 2)
					
					# make sure player is clear of its own shot by making sure hte point is far enough away before it can hurt player...
					if self.player.hitbox.collidepoint(point) and self.player not in hit_sprites:
						self.player.reduce_health(gun_damage, ammo_type)
						hit_sprites.add(self.player)

						
						AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')

					for sprite in self.block_sprites:
						if sprite.hitbox.collidepoint(point):
							return True
					
					for sprite in self.enemy_sprites:
						if sprite.hitbox.collidepoint(point) and sprite not in hit_sprites:
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
							sprite.reduce_health(gun_damage, ammo_type)
							hit_sprites.add(sprite)
			
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
		
	def update(self, dt):
		self.exit_scene()

		self.update_sprites.update(dt)

	def debug(self, debug_list):
		for index, name in enumerate(debug_list):
			self.game.render_text(name, WHITE, self.game.font, (10, 15 * index), True)

	def draw(self, screen):

		self.drawn_sprites.offset_draw(self.player.rect.center)

		self.fade_surf.draw(screen)

		#self.hitscan()
		# if self.player.muzzle_pos is not None:
		# 	pygame.draw.circle(screen, WHITE, self.player.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.player.rect.center - self.drawn_sprites.offset, self.player.muzzle_pos)

		# 	pygame.draw.circle(screen, WHITE, self.guard2.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.guard2.rect.center - self.drawn_sprites.offset, self.guard2.muzzle_pos)

		#pygame.draw.rect(screen, WHITE, ((self.player.hitbox.x - self.drawn_sprites.offset.x, self.player.hitbox.y - self.drawn_sprites.offset.y), (self.player.hitbox.width, self.player.hitbox.height)), 1)
		
		self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
					# str('VEL_X: '+ str(round(self.player.vel.x,3))), 
					# str('VEL_Y: '+str(round(self.player.vel.y,3))),
					str('GUN: '+ str(self.player.gun_index)), 
					str('PLAYER ARMOUR: '+str(self.player.armour)),
					str('PLAYER HEALTH: '+str(self.player.health)),
					None])



