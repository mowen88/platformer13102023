import pygame
from settings import *

class Message(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, text, pos, timer=100, colour=WHITE):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.text = text
		self.pos = pos
		self.timer = timer
		self.colour = colour
		self.alpha = 255

		self.text_surf = self.game.font.render(str(self.text), False, self.colour)
		self.text_rect = self.text_surf.get_rect(center = self.pos)
 
	def update(self, dt):
		self.timer -= dt
		if self.timer < 0:
			self.alpha -= 10 * dt

	def draw(self, screen):
		screen.blit(self.text_surf, self.text_rect)
		self.text_surf.set_alpha(self.alpha)

			
			
			