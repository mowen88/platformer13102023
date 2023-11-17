import pygame
from settings import *

class HUD:
	def __init__(self, game, scene):

		self.game = game
		self.scene = scene
		self.num_of_slots = 3
		self.data = ['health','armour','armour']

	def alpha_rect(self, screen, colour, rect):
		surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
		pygame.draw.rect(surf, colour, surf.get_rect())
		screen.blit(surf, rect)

	def update(self, dt):
		pass

	def draw_boxes(self, screen):
		offset = 70
		max_width = self.num_of_slots * offset
		start_x = (WIDTH - max_width)//2

		for box in range(self.num_of_slots):
			#rect = pygame.draw.rect(screen, BLACK, (start_x + box * offset, 16, 22, 20), border_radius=2)
			icon = pygame.image.load(f'assets/icons/{box}.png').convert_alpha()
			rect = self.alpha_rect(screen, (0, 0, 0, 127), (start_x + box * offset, 16, 50, 20))
			screen.blit(icon, (start_x + box * offset, 16))
			# num_rect = pygame.draw.rect(screen, BLACK, (start_x + 20 + box * offset, 8, 35, 28), border_radius=2)
			self.game.render_text(int(self.scene.player.data[self.data[box]]), WHITE, self.game.font, (start_x + 26 + box * offset, 16), True)


	def draw(self, screen):
		self.draw_boxes(screen)