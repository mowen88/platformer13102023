import pygame, threading, csv, math, random, time
from math import atan2, degrees, pi
from state import State
from settings import *

from pytmx.util_pygame import load_pygame
from timer import Timer
from message import Message
from camera import Camera
from pause import PauseMenu
from inventory import Inventory
from hud import HUD
from player import Player
from enemy import Guard
from sprites import FadeSurf, HurtSurf, Collider, Tile, Tutorial, SecretTile, AnimatedTile, Liquid, AnimatedPickup, Platform, Barrel, MovingPlatform, Door, Trigger, Barrier, Laser, Lever
from weapons import Gun 
from bullets import BlasterBullet, HyperBlasterBullet, Grenade
from particles import DustParticle, GibbedChunk, MuzzleFlash, FadeParticle, ShotgunParticle, RocketParticle, RailParticle, Explosion, Flash

class Scene(State):
	def __init__(self, game, prev_level, current_scene, entry_point):
		State.__init__(self, game)

	
		self.game = game
		self.prev_level = prev_level
		self.current_scene = current_scene
		self.entry_point = entry_point
		self.scene_size = self.get_scene_size()
		SAVE_DATA.update({'current_scene': self.current_scene, 'entry_pos': self.entry_point})
		
		if SCENE_DATA[self.current_scene]['level'] != self.prev_level:
			self.game.play_music(SCENE_DATA[self.current_scene]['track'])

		if self.current_scene not in SAVE_DATA['scenes_completed']:
			SAVE_DATA['scenes_completed'].append(self.current_scene)
	
		self.screenshaking = False
		self.screenshake_timer = 0

		self.update_sprites = pygame.sprite.Group()
		self.drawn_sprites = Camera(self.game, self)
		self.visible_window = pygame.Rect(VISIBLE_WINDOW_RECT)
		self.audible_distance = pygame.Rect(AUDIBLE_WINDOW_RECT)

		self.bg_sprites = pygame.sprite.Group()
		self.tutorial_sprites = pygame.sprite.Group()
		self.block_sprites = pygame.sprite.Group()
		self.exit_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		self.ladder_sprites = pygame.sprite.Group()
		
		self.enemy_sprites = pygame.sprite.Group()
		self.gun_sprites = pygame.sprite.Group()
		self.bullet_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		self.liquid_sprites = pygame.sprite.Group()
		self.pickup_sprites = pygame.sprite.Group()
		self.destructible_sprites = pygame.sprite.Group()
		self.secret_sprites = pygame.sprite.Group()
		self.trigger_sprites = pygame.sprite.Group()
		self.barrier_sprites = pygame.sprite.Group()

		# fade screen and exit flag
		self.message = None
		self.fade_surf = FadeSurf(self.game, self, [self.update_sprites], (RES/2))
		self.hurt_surf = HurtSurf(self.game, self, [self.update_sprites], (RES/2))
		self.get_fog_surf()
		
		self.exiting = False

		self.quad_timer = Timer(1440, 20, 12)
		self.invulnerability_timer = Timer(1440, 20, 12)
		self.breathe_timer = Timer(200, 60, 12)
		self.rebreather_timer = Timer(720, 20, 12)
		self.envirosuit_timer = Timer(720, 20, 12)

		#self.all_chunks = self.split_scene_into_grid()
		
		# create all objects in the scene using tmx data
		self.tmx_data = load_pygame(f'scenes/{self.current_scene}/{self.current_scene}.tmx')

		self.hud = HUD(self.game, self)
		self.save_point = self.get_save_point()

		# wait for instances to load in
		self.thread = threading.Thread(target=self.create_scene_instances)
		self.thread.start()
		self.thread.join()

		self.player.hitbox.topleft = self.start_pos
		self.drawn_sprites.offset = pygame.math.Vector2(self.player.rect.centerx - HALF_WIDTH, self.player.rect.centery - HALF_HEIGHT)

	def get_save_point(self):
		if SCENE_DATA[self.current_scene]['level'] != self.prev_level:
			COMMIT_SAVE_DATA.update(SAVE_DATA)
			COMMIT_AMMO_DATA.update(AMMO_DATA)
			self.game.write_data()
			self.message = Message(self.game, self, [self.update_sprites], SCENE_DATA[self.current_scene]['level'], (HALF_WIDTH, HALF_HEIGHT - TILESIZE * 2), 220)

	def get_fog_surf(self):
		self.glow_surf = pygame.Surface(self.scene_size)
		self.light_mask = pygame.image.load('assets/circle.png').convert_alpha()
		self.light_rect = self.light_mask.get_rect()

	def render_fog(self, target, colour, screen):
		self.glow_surf.fill(colour)
		self.light_rect.center = target.rect.center - self.drawn_sprites.offset
		self.glow_surf.blit(self.light_mask, self.light_rect)
		screen.blit(self.glow_surf, (0,0), special_flags = pygame.BLEND_MULT)

	def create_scene(self, level, scene):
		# unit = self.current_unit if unit != self.current_unit else self.current_unit
		# level = self.current_level if level != self.current_level else self.current_level
		Scene(self.game, level, scene, self.entry_point).enter_state()

	def respawn(self):
		self.game.read_data()
		self.game.stack.pop()
		Scene(self.game, SCENE_DATA[SAVE_DATA['current_scene']]['level'], SAVE_DATA['current_scene'], SAVE_DATA['entry_pos']).enter_state()
	
	def get_scene_size(self):
		with open(f'scenes/{self.current_scene}/{self.current_scene}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		return (cols * TILESIZE, rows * TILESIZE)

	# def split_scene_into_grid(self, grid_size=(12 * TILESIZE, 6 * TILESIZE)):
	#     scene_width, scene_height = self.get_scene_size()
	#     grid_x, grid_y = grid_size

	#     sections_x = scene_width//grid_x
	#     sections_y = scene_height//grid_y

	#     grid = []
	#     for row in range(grid_y):
	#         for col in range(grid_x):
	#             x = col * grid_x
	#             y = row * grid_y
	#             rect = pygame.Rect(x, y, grid_x, grid_y)
	#             #pygame.draw.rect(self.game.screen, WHITE, rect, 2)
	#             grid.append(rect)

	#     return grid

	def create_scene_instances(self):

		gun_list = list(CONSTANT_DATA['guns'].keys())
		ammo_list = list(AMMO_DATA.keys())
		armour_list = list(ARMOUR_DATA.keys())
		health_list = list(HEALTH_DATA.keys())
		item_list = CONSTANT_DATA['all_items']
		tutorials_list = list(TUTORIALS.keys())

		layers = []
		for layer in self.tmx_data.layers:
			layers.append(layer.name)

		if 'secret' in layers:
			for x, y, surf in self.tmx_data.get_layer_by_name('secret').tiles():
				SecretTile(self.game, self, [self.block_sprites, self.secret_sprites, self.update_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf)

		if 'blocks' in layers:
			for x, y, surf in self.tmx_data.get_layer_by_name('blocks').tiles():
				Tile([self.block_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['blocks'])

		if 'bg' in layers:
			for x, y, surf in self.tmx_data.get_layer_by_name('bg').tiles():
				Tile([self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['background'])

		
		if 'ladders' in layers:
			for x, y, surf in self.tmx_data.get_layer_by_name('ladders').tiles():
				Tile([self.ladder_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['objects'])

		if 'tutorials' in layers:
			for obj in self.tmx_data.get_layer_by_name('tutorials'):
				if obj.name not in SAVE_DATA['killed_sprites']:
					for tutorial in tutorials_list:
						if obj.name == tutorial: Tutorial([self.tutorial_sprites], (obj.x, obj.y, obj.width, obj.height), TUTORIALS[tutorial])

		if 'pickups' in layers:
			for obj in self.tmx_data.get_layer_by_name('pickups'):
				if obj.name not in SAVE_DATA['killed_sprites']:
					for num in range(100): # range must cover the amount of the most numerous pickup
						for gun in gun_list:
							if obj.name == f'{gun}_{num}': AnimatedPickup(self.game, self, [self.pickup_sprites, self.update_sprites, self.drawn_sprites],\
							(obj.x, obj.y),LAYERS['objects'], f'assets/pickups/{obj.name.split("_")[0]}', 'loop', obj.name)
						for armour in armour_list:
							if obj.name == f'{armour}_{num}': AnimatedPickup(self.game, self, [self.pickup_sprites, self.update_sprites, self.drawn_sprites],\
							(obj.x, obj.y), LAYERS['objects'], f'assets/pickups/{obj.name.split("_")[0]}', 'loop', obj.name)
						for ammo in ammo_list:
							if obj.name == f'{ammo}_{num}': AnimatedPickup(self.game, self, [self.pickup_sprites, self.update_sprites, self.drawn_sprites],\
							(obj.x, obj.y), LAYERS['objects'], f'assets/pickups/{obj.name.split("_")[0]}', 'loop', obj.name, False)
						for health in health_list:
							if obj.name == f'{health}_{num}': AnimatedPickup(self.game, self, [self.pickup_sprites, self.update_sprites, self.drawn_sprites],\
							(obj.x, obj.y), LAYERS['objects'], f'assets/pickups/{obj.name.split("_")[0]}', 'loop', obj.name, False)
						for item in item_list:
							if obj.name == f'{item}_{num}': AnimatedPickup(self.game, self, [self.pickup_sprites, self.update_sprites, self.drawn_sprites],\
							(obj.x, obj.y), LAYERS['objects'], f'assets/pickups/{obj.name.split("_")[0]}', 'loop', obj.name)

		if 'platforms' in layers:
			for obj in self.tmx_data.get_layer_by_name('platforms'):
				if obj.name == '1': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (0.02, 0), 80)
				if obj.name == '2': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (0, 0.02), 64)
				if obj.name == '3': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (0.01, 0), 64)
				if obj.name == '4': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (-0.025, 0.025), 48, 'circular')
				if obj.name == '5': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (0, 0.025), 64)
				if obj.name == '6': MovingPlatform(self, [self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'], (0.025, -0.025), 48, 'circular')
				# static platforms and crates
				if obj.name == '7': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/1.png').convert_alpha(), LAYERS['objects'])
				if obj.name == '8': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'red_crate': Platform(self, [self.platform_sprites,self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/red_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'blue_crate': Platform(self, [self.platform_sprites,self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/blue_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'green_crate': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/green_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'grey_crate': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/grey_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'red_small_crate': Platform(self, [self.platform_sprites,self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/red_small_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'grey_small_crate': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/red_small_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'blue_small_crate': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/red_small_crate.png').convert_alpha(), LAYERS['objects'])
				if obj.name == 'green_small_crate': Platform(self, [self.platform_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/crates/red_small_crate.png').convert_alpha(), LAYERS['objects'])
				# barrels
				if obj.name == 'barrel': Barrel(self, [self.destructible_sprites, self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
					pygame.image.load('assets/objects/barrel.png').convert_alpha(), LAYERS['objects'])


		if 'triggers' in layers:
			for obj in self.tmx_data.get_layer_by_name('triggers'):
				for num in range(100):
					if obj.name == f'trigger_{num}': Trigger(self.game, self, [self.trigger_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), LAYERS['objects'], f'assets/triggers/trigger_{num}', 'loop', f'trigger_{num}')
					if obj.name == f'button_{num}': Trigger(self.game, self, [self.trigger_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), LAYERS['objects'], f'assets/triggers/button_{num}', 'loop', f'button_{num}')
					if obj.name == f'barrier_{num}': Barrier(self.game, self, [self.barrier_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), LAYERS['objects'], f'assets/barriers/{num}', 'loop', num)
					if obj.name == f'laser_{num}': Laser(self.game, self, [self.barrier_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), LAYERS['objects'], f'assets/lasers/{num}', 'loop', num)

			
		# add the player, must be after moving platforms so the player speed and position matches correctly (due to update order)
		if 'entries' in layers:
			for obj in self.tmx_data.get_layer_by_name('entries'):
				if obj.name == self.entry_point:
					self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'player', LAYERS['player'])
					#self.player.hitbox.topleft = (obj.x, obj.y)
					self.start_pos = (obj.x, obj.y)

		key_dict = {'3':'blue key'}
		if 'exits' in layers:
			for obj in self.tmx_data.get_layer_by_name('exits'):
				for num in range(100):
					key_name = key_dict[str(num)] if str(num) in list(key_dict.keys()) else None

					if obj.name.split("_")[0] == str(num): Door(self.game, self, [self.exit_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y),\
											LAYERS['objects'], f'assets/doors/{obj.name.split("_")[0]}', 'loop', obj.name, key_name)

		if 'liquid' in layers:
			for obj in self.tmx_data.get_layer_by_name('liquid'):
				if obj.name == 'water': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)
				if obj.name == 'water_top': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)
				if obj.name == 'slime': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)
				if obj.name == 'slime_top': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)
				if obj.name == 'lava': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)
				if obj.name == 'lava_top': Liquid([self.liquid_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.image, LAYERS['liquid'], obj.name)

		if 'entities' in layers:
			for obj in self.tmx_data.get_layer_by_name('entities'):
				if obj.name == 'collider': Collider([self.update_sprites, self.collision_sprites], (obj.x, obj.y), (obj.width, obj.height))
				if obj.name == 'guard': self.guard = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
				if obj.name == 'sg_guard':self.guard2 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
				if obj.name == 'gladiator':self.guard3 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
				if obj.name == 'enforcer':self.guard3 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
				#if obj.name == 'lever': Lever(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'assets/objects/lever.png', LAYERS['player'])
				#if obj.name == 'bg': self.bg = Tile([self.drawn_sprites], (obj.x -1, obj.y -1), pygame.image.load(f'scenes/{self.current_scene}/bg.png').convert_alpha(), LAYERS['background'])
				
		# create gun objects for the enemies and player
		self.create_player_gun()
		self.create_enemy_guns()

		#Tile([self.drawn_sprites], (0,0), pygame.image.load(f'scenes/{self.current_scene}/{self.current_scene}.png'), LAYERS['background'])

	def create_player_gun(self):
		self.player.gun_sprite = Gun(self.game, self, self.player, [self.gun_sprites, self.update_sprites, self.drawn_sprites], self.player.hitbox.center, LAYERS['particles'])

	def create_enemy_guns(self):
		for sprite in self.enemy_sprites:
			sprite.gun_sprite = Gun(self.game, self, sprite, [self.gun_sprites, self.update_sprites, self.drawn_sprites], sprite.hitbox.center, LAYERS['particles'])

	def create_bullet(self, sprite, auto=False):

		# reset the firing button if the weapon is not an automatic
		if sprite == self.player:

			ammo_type = CONSTANT_DATA['guns'][sprite.gun]['ammo_type']
			ammo_used = CONSTANT_DATA['guns'][sprite.gun]['ammo_used']

			AMMO_DATA[ammo_type] -= ammo_used
			SAVE_DATA.update({'ammo': max(AMMO_DATA[ammo_type], AMMO_DATA[ammo_type])})

			if not auto:
				ACTIONS['left_click'] = False

		if sprite.gun == 'blaster':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites],sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}',sprite)
			BlasterBullet(self.game, self, sprite, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], 6)
			self.game.weapon_fx['blaster'].play()

		elif sprite.gun == 'hyper blaster':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites],sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}',sprite)
			HyperBlasterBullet(self.game, self, sprite, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], 10, sprite)

		elif sprite.gun in ['hand grenade', 'grenade launcher']:

			speed = 7 if sprite.gun in ['grenade launcher'] else 4
			Grenade(self.game, self, sprite, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], sprite.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], speed)
			self.game.weapon_fx['throw_grenade'].play()

		elif sprite.gun in ['shotgun', 'super shotgun']:

			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			self.game.weapon_fx['shotgun'].play()

			lower = -2 # if sprite.gun == 'shotgun' else -4
			upper = 3 # if sprite.gun == 'shotgun' else 6 

			spread_offset = 0.04 if sprite.gun == 'shotgun' else 0.1
			
			for pellet in range(lower, upper):
				pellet *= spread_offset
				self.hitscan(sprite, pellet)


		elif sprite.gun == 'machine gun':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			self.game.weapon_fx['machine gun'].play()
			self.hitscan(sprite, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'chain gun':
			MuzzleFlash(self.game, self, [self.update_sprites, self.drawn_sprites], sprite.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}', sprite)
			self.hitscan(sprite, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'railgun':
			self.hitscan(sprite)

	def create_particle(self, particle_type, pos):
		if particle_type == 'landing':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/landing')

		elif particle_type == 'blood':
			AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/blood')

		elif particle_type == 'blaster':
			FadeParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], None, YELLOW)


		elif particle_type == 'jump':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/jump')

		elif particle_type == 'double_jump':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/double_jump')

		elif particle_type == 'explosion':
			Explosion(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/mushroom')
			self.game.weapon_fx['explode'].play()

		elif particle_type == 'flash':
			Flash(self.game, self, [self.update_sprites, self.drawn_sprites], pos, WHITE, 8, LAYERS['foreground'])
		elif particle_type == 'splash':
			DustParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/splash')
		elif particle_type == 'chunk':
			for chunk in range(random.randint(8,12)):
				GibbedChunk(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], f'assets/particles/chunk')
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
			gun_damage = CONSTANT_DATA['guns'][self.player.gun]['damage']
			angle = math.atan2(pygame.mouse.get_pos()[1]-sprite.gun_sprite.rect.centery + self.drawn_sprites.offset[1],\
					pygame.mouse.get_pos()[0]-sprite.gun_sprite.rect.centerx + self.drawn_sprites.offset[0])
		else:
			gun_damage = CONSTANT_DATA['enemies'][sprite.name]['damage']
			angle = math.atan2(self.player.rect.centery-self.drawn_sprites.offset[1]-sprite.gun_sprite.rect.centery + self.drawn_sprites.offset[1],\
					self.player.rect.centerx-self.drawn_sprites.offset[0]-sprite.gun_sprite.rect.centerx + self.drawn_sprites.offset[0])

		x = math.hypot(WIDTH, HEIGHT) * math.cos(angle + offset) + sprite.gun_sprite.rect.centerx
		y = math.hypot(WIDTH, HEIGHT) * math.sin(angle + offset) + sprite.gun_sprite.rect.centery

		distance = ((x, y) - pygame.math.Vector2(sprite.gun_sprite.rect.center)).magnitude()

		
		ammo_type = CONSTANT_DATA['guns'][sprite.gun]['ammo_type']

		if sprite.gun in ['shotgun', 'super shotgun', 'machine gun', 'chain gun']:

			point_list = self.get_equidistant_points(sprite.gun_sprite.rect.center, (x, y), int(distance/3))
			for num, point in enumerate(point_list):

				if num > 6:

					# make sure player is clear of its own shot by making sure the point is far enough away before it can hurt player...
					if self.player.hitbox.collidepoint(point):
						if sprite.gun in ['shotgun', 'super shotgun']:
							gun_damage = round(gun_damage/(num * 0.1))
						self.player.reduce_health(gun_damage, ammo_type)
						if gun_damage > 0:
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
						return True

					for sprite in self.destructible_sprites:
						if sprite.hitbox.collidepoint(point):
							sprite.exploded = True
							return True

					for sprite in self.trigger_sprites:
						if sprite.hitbox.collidepoint(point) and 'button' in sprite.name:
							sprite.activated = True
							for barrier in self.barrier_sprites:
								if barrier.name == int(sprite.name.split("_")[1]):
									barrier.activated = True


					for sprite in self.secret_sprites:
						if sprite.hitbox.collidepoint(point):
							ShotgunParticle(self.game, self, [self.update_sprites, self.drawn_sprites], point_list[num-1], LAYERS['particles'])
							sprite.activated = True
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

					for sprite in self.destructible_sprites:
						if sprite.hitbox.collidepoint(point):
							sprite.exploded = True

					for sprite in self.secret_sprites:
						if sprite.hitbox.collidepoint(point):
							sprite.activated = True
							return True

					for sprite in self.block_sprites:
						if sprite.hitbox.collidepoint(point):
							return True

					for sprite in self.secret_sprites:
						if sprite.hitbox.collidepoint(point):
							sprite.activated = True
							return True
					
					for sprite in self.enemy_sprites:
						if sprite.hitbox.collidepoint(point) and sprite not in hit_sprites:
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
							sprite.reduce_health(gun_damage, ammo_type)
							hit_sprites.add(sprite)
			
							AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
	
	def upgrade_timers(self, screen):

		if self.player.quad_damage:
			self.render_fog(self.player, (0,0,255), screen)
			self.game.render_text(str(round(self.quad_timer.countdown)), WHITE, self.game.ui_font, (WIDTH - TILESIZE * 2, HEIGHT - TILESIZE))
		if self.player.invulnerable:
			self.render_fog(self.player, (255, 0, 0), screen)
			self.game.render_text(str(round(self.invulnerability_timer.countdown)), WHITE, self.game.ui_font, (WIDTH - TILESIZE * 2, HEIGHT - TILESIZE * 2))
		if self.player.rebreather:
			self.render_fog(self.player, (NEON_BLUE), screen)
			self.game.render_text(str(round(self.rebreather_timer.countdown)), WHITE, self.game.ui_font, (WIDTH - TILESIZE * 2, HEIGHT - TILESIZE * 2))
		if self.player.envirosuit:
			self.render_fog(self.player, (NEON_GREEN), screen)
			self.game.render_text(str(round(self.envirosuit_timer.countdown)), WHITE, self.game.ui_font, (WIDTH - TILESIZE * 2, HEIGHT - TILESIZE * 2))
		
	def pause_or_inventory(self, actions, menu_type):
		for i in actions:
			if i:
				menu_type.enter_state()
				self.game.reset_keys()

	def screenshake(self, dt):
		if self.screenshaking:
			self.screenshake_timer += dt
			if self.screenshake_timer < 35: 
				self.drawn_sprites.offset += [random.randint(-2, 2), random.randint(-2, 2)]
			else: 
				self.screenshaking = False
				self.screenshake_timer = 0

	def next_track(self):
		if not pygame.mixer.music.get_busy():
			self.game.track_index += 1
			if self.game.track_index >= len(list(TRACKS.keys()))-1:
				self.game.track_index = 0
			self.game.play_music(self.game.track_index)

	def update(self, dt):
		self.next_track()
		
		# respawn if bug !?
		if ACTIONS['r']:
			self.respawn()
			ACTIONS['r'] = False

		self.screenshake(dt)

		self.pause_or_inventory([ACTIONS['space']], PauseMenu(self.game))
		self.pause_or_inventory([ACTIONS['e'],ACTIONS['tab']], Inventory(self.game, self))
		self.hud.update(dt)
		self.update_sprites.update(dt)

		#print(round(self.game.clock.get_fps(), 2))

		# update quad damage timer
		self.player.quad_damage = True if self.quad_timer.update(dt) else False
		self.player.invulnerable = True if self.invulnerability_timer.update(dt) else False
		self.player.underwater = True if self.breathe_timer.update(dt) else False
		self.player.rebreather = True if self.rebreather_timer.update(dt) else False
		self.player.envirosuit = True if self.envirosuit_timer.update(dt) else False

		self.visible_window.center = self.player.rect.center
		self.audible_distance.center = self.player.rect.center


	def debug(self, debug_list):
		for index, name in enumerate(debug_list):
			self.game.render_text(name, WHITE, self.game.font, (10, 15 * index), True)

	def draw(self, screen):

		self.drawn_sprites.offset_draw(self.player.rect.center)

		self.upgrade_timers(screen)

		if self.player.hurt and not self.player.invulnerable:
			self.hurt_surf.draw(screen)

		if self.message:
			self.message.draw(screen)

		self.hud.draw(screen)
		self.fade_surf.draw(screen)

		# self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
		# 			str('entry_point: '+ str(self.entry_point)), 
		# 			str('gun: '+ str(self.player.gun)),
		# 			str('unit: '+ str(SCENE_DATA[self.current_scene]['unit'])),
		# 			str('on ground: '+ str(self.player.state)),
		# 			str('breathe timer: '+ str(self.breathe_timer.timer)),
		# 			str('track_index: '+ str(self.game.track_index)),
		# 			# str('PLAYER HEALTH: '+str(self.player.health)),
		# 			None])



