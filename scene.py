import pygame, math, random
from math import atan2, degrees, pi
from state import State
from settings import *

from pytmx.util_pygame import load_pygame

from camera import Camera
from player import Player
from enemy import Guard
from sprites import Collider, Tile, AnimatedTile, MovingPlatform
from weapons import Gun 
from bullets import BlasterBullet
from particles import MuzzleFlash, FadeParticle, ShotgunParticle, RocketParticle, RailParticle

class Scene(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.update_sprites = pygame.sprite.Group()
		self.drawn_sprites = Camera(self.game, self)

		self.block_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		self.ladder_sprites = pygame.sprite.Group()
		
		self.enemy_sprites = pygame.sprite.Group()
		self.gun_sprites = pygame.sprite.Group()
		self.bullet_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		self.create_map()

	def create_map(self):

		tmx_data = load_pygame('scenes/0/0.tmx')

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
			if obj.name == '0': self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'player', LAYERS['player'])
			if obj.name == 'guard': self.guard = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
			if obj.name == 'sg_guard':self.guard2 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
		
		for sprite in self.enemy_sprites:
			self.create_enemy_guns(sprite)
		self.create_player_gun()

	def create_player_gun(self):
		self.gun_sprite = Gun(self.game, self, self.player, [self.gun_sprites, self.update_sprites, self.drawn_sprites], self.player.hitbox.center, LAYERS['particles'])

	def create_enemy_guns(self, sprite):
		Gun(self.game, self, sprite, [self.gun_sprites, self.update_sprites, self.drawn_sprites], sprite.hitbox.center, LAYERS['particles'])

	def create_bullet(self, sprite, auto=False):
		# reset the firing button if the weapon is not an automatic
		if not auto:
			ACTIONS['left_click'] = False

		if sprite.gun == 'blaster':
			MuzzleFlash(self.game, self, self.player, [self.update_sprites, self.drawn_sprites], self.player.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}')
			BlasterBullet(self.game, self, self.player, [self.bullet_sprites, self.update_sprites, self.drawn_sprites], self.player.muzzle_pos + self.drawn_sprites.offset, LAYERS['particles'])

		elif sprite.gun == 'shotgun':
			MuzzleFlash(self.game, self, self.player, [self.update_sprites, self.drawn_sprites], self.player.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}')
			spread = 0.04
			for shot in range(-2, 3, 1):
				shot *= spread
				self.hitscan(sprite.gun, shot)

		elif sprite.gun == 'machine gun':
			MuzzleFlash(self.game, self, self.player, [self.update_sprites, self.drawn_sprites], self.player.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}')
			self.hitscan(sprite.gun, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'chain gun':
			
			MuzzleFlash(self.game, self, self.player, [self.update_sprites, self.drawn_sprites], self.player.muzzle_pos, LAYERS['particles'], f'assets/muzzle_flash/{sprite.gun}')
			self.hitscan(sprite.gun, random.uniform(-0.04, 0.04))

		elif sprite.gun == 'railgun':
			self.hitscan('railgun')

	def create_particle(self, particle_type, pos):
		if particle_type == 'blaster':
			FadeParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], YELLOW)
		else:
			FadeParticle(self.game, self, [self.update_sprites, self.drawn_sprites], pos, LAYERS['particles'], WHITE)

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

	def hitscan(self, gun, offset=0):
		angle = math.atan2(pygame.mouse.get_pos()[1]-self.gun_sprite.rect.centery + self.drawn_sprites.offset[1],\
				pygame.mouse.get_pos()[0]-self.gun_sprite.rect.centerx + self.drawn_sprites.offset[0])

		x = math.hypot(WIDTH, HEIGHT) * math.cos(angle + offset) + self.gun_sprite.rect.centerx
		y = math.hypot(WIDTH, HEIGHT) * math.sin(angle + offset) + self.gun_sprite.rect.centery

		distance = ((x, y) - pygame.math.Vector2(self.gun_sprite.rect.center)).magnitude()

		if gun == 'shotgun' or gun == 'machine gun' or gun == 'chain gun':

			point_list = self.get_equidistant_points(self.gun_sprite.rect.center, (x, y), int(distance/3))
			for num, point in enumerate(point_list):
				for sprite in self.block_sprites:
					if sprite.hitbox.collidepoint(point):
						ShotgunParticle(self.game, self, [self.update_sprites, self.drawn_sprites], point_list[num-1], LAYERS['particles'])
						return True
				for sprite in self.enemy_sprites:
					if sprite.hitbox.collidepoint(point):
						AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')
						return True

		elif gun == 'railgun':

			point_list = self.get_equidistant_points(self.gun_sprite.rect.center, (x, y), int(distance/8))
			for num, point in enumerate(point_list):
				if num >= 3 and num <= len(point_list)-2:
					RailParticle(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], num) #pygame.draw.circle(self.game.screen, NEON_BLUE, point - self.drawn_sprites.offset, 2)
				for sprite in self.block_sprites:
					if sprite.hitbox.collidepoint(point):
						return True
				for sprite in self.enemy_sprites:
					if sprite.hitbox.collidepoint(point):
						AnimatedTile(self.game, self, [self.update_sprites, self.drawn_sprites], point, LAYERS['particles'], f'assets/particles/blood')

	def update(self, dt):

		if ACTIONS['space']:
			self.exit_state()
			ACTIONS['space'] = False

		self.update_sprites.update(dt)

	def debug(self, debug_list):
		for index, name in enumerate(debug_list):
			self.game.render_text(name, BLACK, self.game.font, (10, 15 * index))

	def draw(self, screen):

		self.drawn_sprites.offset_draw(self.player.rect.center)

		#self.hitscan()
		# if self.player.muzzle_pos is not None:
		# 	pygame.draw.circle(screen, WHITE, self.player.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.player.rect.center - self.drawn_sprites.offset, self.player.muzzle_pos)

		# 	pygame.draw.circle(screen, WHITE, self.guard2.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.guard2.rect.center - self.drawn_sprites.offset, self.guard2.muzzle_pos)

		#pygame.draw.rect(screen, WHITE, ((self.player.hitbox.x - self.drawn_sprites.offset.x, self.player.hitbox.y - self.drawn_sprites.offset.y), (self.player.hitbox.width, self.player.hitbox.height)), 1)
		
		self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
					str('VEL_X: '+ str(round(self.player.vel.x,3))), 
					str('VEL_Y: '+str(round(self.player.vel.y,3))),
					str('CYOTE TIMER: '+str(self.guard.facing)),
					None])



