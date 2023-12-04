import pygame
from state import State
from settings import *

class Intermission(State):
	def __init__(self, game, scene, new_scene):
		State.__init__(self, game)

		if len(self.game.stack) > 1:
			self.game.stack.pop()

		self.game = game
		self.scene = scene
		self.new_scene = new_scene

	def update(self, dt):
		if ACTIONS['enter']:
			self.scene.create_scene(self.scene.prev_level, self.new_scene)
			ACTIONS['enter'] = False

	def draw(self, screen):
		screen.fill(DARK_GREEN)
		self.game.render_text(f'You are now heading to the {SCENE_DATA[self.scene.new_scene]["unit"]}.', NEON_GREEN, self.game.font, (HALF_WIDTH, HALF_HEIGHT - TILESIZE))
		self.game.render_text('Press enter to continue...', NEON_GREEN, self.game.font, (HALF_WIDTH, HALF_HEIGHT + TILESIZE))