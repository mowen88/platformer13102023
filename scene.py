import pygame
from state import State
from settings import *

from pytmx.util_pygame import load_pygame

from camera import Camera
from player import Player
from enemy import Guard
from sprites import Tile, MovingPlatform
from weapons import Gun

class Scene(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.update_sprites = pygame.sprite.Group()
		self.drawn_sprites = Camera(self.game, self)

		self.block_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		
		self.enemy_sprites = pygame.sprite.Group()
		self.gun_sprites = pygame.sprite.Group()
		

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

		for obj in tmx_data.get_layer_by_name('entities'):
			if obj.name == '0': self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (obj.x, obj.y), 'player', LAYERS['player'])
			if obj.name == 'guard': self.guard = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
			if obj.name == 'sg_guard':self.guard2 = Guard(self.game, self, [self.enemy_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), obj.name, LAYERS['player'])
			
		self.create_guns()

	def create_guns(self):
		for sprite in self.drawn_sprites:
			if sprite == self.player:
				self.gun_sprite = Gun(self.game, self, sprite.gun, sprite, [self.gun_sprites, self.update_sprites, self.drawn_sprites], sprite.hitbox.center, LAYERS['particles'])
			elif hasattr(sprite, 'gun'):
				Gun(self.game, self, sprite.gun, sprite, [self.gun_sprites, self.update_sprites, self.drawn_sprites], sprite.hitbox.center, LAYERS['particles'])

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

		# if self.guard.muzzle_pos is not None:
		# 	pygame.draw.circle(screen, WHITE, self.guard.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.guard.rect.center - self.drawn_sprites.offset, self.guard.muzzle_pos)

		# 	pygame.draw.circle(screen, WHITE, self.guard2.muzzle_pos, 5)
		# 	pygame.draw.line(screen, WHITE, self.guard2.rect.center - self.drawn_sprites.offset, self.guard2.muzzle_pos)

		self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
					str('VEL_X: '+ str(round(self.player.vel.x,3))), 
					str('VEL_Y: '+str(round(self.player.vel.y,3))),
					str('CYOTE TIMER: '+str(self.guard.state)),
					None])



