import pygame
from settings import *

class Message(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, text, pos):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.text = text
		self.pos = pos
		self.timer = 100

	def update(self, dt):
		self.timer -= dt

	def draw(self, screen):
		if self.timer > 0:
			self.game.render_text(self.text, WHITE, self.game.font, self.pos)