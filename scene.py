import pygame
from state import State
from settings import *

from pytmx.util_pygame import load_pygame

from camera import Camera
from player import Player
from sprites import Tile, MovingPlatform

class Scene(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.update_sprites = pygame.sprite.Group()
		self.drawn_sprites = Camera(self.game, self)

		self.block_sprites = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()
		

		self.create_map()

	def create_map(self):

		tmx_data = load_pygame('scenes/0/0.tmx')

		

		for x, y, surf in tmx_data.get_layer_by_name('blocks').tiles():
			Tile([self.block_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf, LAYERS['blocks'])

		for obj in tmx_data.get_layer_by_name('platforms'):
			if obj.name == '1': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0.05, 0), 80)
			if obj.name == '2': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0, 0.02), 64)
			if obj.name == '3': MovingPlatform([self.platform_sprites, self.update_sprites, self.drawn_sprites], (obj.x, obj.y), pygame.image.load('assets/platforms/0.png').convert_alpha(), LAYERS['blocks'], (0.01, 0), 64)


		self.player = Player(self.game, self, [self.update_sprites, self.drawn_sprites], (100,100), 'player', LAYERS['player'])

	def update(self, dt):

		if ACTIONS['space']:
			self.exit_state()
			ACTIONS['space'] = False

		self.update_sprites.update(dt)

	def debug(self, debug_list):
		for index, name in enumerate(debug_list):
			self.game.render_text(name, BLACK, self.game.font, (10, 20 * index))

	def draw(self, screen):

		self.drawn_sprites.offset_draw(self.player.rect.center)

		self.debug([str('FPS: '+ str(round(self.game.clock.get_fps(), 2))),
					str('VEL X: '+ str(round(self.player.vel.x,3))), 
					str('VEL Y: '+str(round(self.player.vel.y,3))),
					str('PLATFORM: '+str(self.player.on_ground)),

					None])


