import pygame
from state import State
from settings import *

class Intermission(State):
	def __init__(self, game, scene, new_scene):
		State.__init__(self, game)

		self.game = game
		self.scene = scene
		self.new_scene = new_scene

	def update(self, dt):
		if ACTIONS['enter']:
			self.scene.create_scene(self.scene.prev_level, self.new_scene)
			ACTIONS['enter'] = False

	def draw(self, screen):
		screen.fill(BLACK)
		self.game.render_text(f'You are now heading to the {SCENE_DATA[self.scene.new_scene]['unit']}.', WHITE, self.game.ui_font, (HALF_WIDTH, HALF_HEIGHT - TILESIZE))
		self.game.render_text('Press enter to continue...', WHITE, self.game.ui_font, (HALF_WIDTH, HALF_HEIGHT + TILESIZE))