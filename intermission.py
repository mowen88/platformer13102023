import pygame
from state import State
from settings import *

from dialogue import Dialogue

class Block(pygame.sprite.Sprite):
	def __init__(self, pos, name):
		self.image = pygame.Surface((TILESIZE, TILESIZE))
		self.image.fill(NEON_GREEN)
		self.rect = self.image.get_rect(center = pos)
		self.name = name

class Intermission(State):
	def __init__(self, game, scene, new_scene):
		State.__init__(self, game)

		if len(self.game.stack) > 1:
			self.game.stack.pop()

		self.game = game
		self.scene = scene
		self.new_scene = new_scene
		self.text = ['[ You are entering', f'the {SCENE_DATA[self.scene.new_scene]["level"]} ]']

		self.dialogue =Dialogue(self.game, self.scene, self.text, 600)

	def draw_mission_blocks(self, screen):
		units = {'unit 1':[20, 200], 'unit 2':[80, 150], 'unit 3':[120, 150], 'unit 4':[220, 120], 'unit 5':[300, 100], 'unit 6':[350, 80], 'unit 7':[380, 40]}
		for unit, pos in units.items():
			block = Block(pos, unit)
			screen.blit(block.image, block.rect)

	def update(self, dt):
		if ACTIONS['enter']:
			self.scene.create_scene(self.scene.prev_level, self.new_scene)
			ACTIONS['enter'] = False

		self.dialogue.update(dt)

	def draw(self, screen):
		screen.fill(DARK_GREEN)
		self.draw_mission_blocks(screen)
		self.dialogue.draw(screen)
		# self.game.render_text(f'You are now heading to the {SCENE_DATA[self.scene.new_scene]["unit"]}.', NEON_GREEN, self.game.font, (HALF_WIDTH, HALF_HEIGHT - TILESIZE))
		# self.game.render_text('Press enter to continue...', NEON_GREEN, self.game.font, (HALF_WIDTH, HALF_HEIGHT + TILESIZE))