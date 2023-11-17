import pygame
from settings import *

class HUD:
	def __init__(self, game, zone):

		self.game = game
		self.zone = zone
		self.num_of_slots = 3
		self.colours = [NEON_GREEN, WHITE, NEON_BLUE]

	def update(self, dt):
		pass

	def draw_boxes(self, screen):
		offset = 70
		max_width = self.num_of_slots * offset
		start_x = (WIDTH - max_width)//2

		for box in range(self.num_of_slots):
			img_rect = pygame.draw.rect(screen, BLACK, (start_x + box * offset, 18, 22, 20), border_radius=2)
			num_rect = pygame.draw.rect(screen, BLACK, (start_x + 20 + box * offset, 10, 35, 28), border_radius=2)
			self.game.render_text('000', self.colours[box], self.game.font, (num_rect.center))

		item_in_use = pygame.draw.rect(screen, BLACK, (300, 18, 20, 20), border_radius=2)

	def draw(self, screen):
		self.draw_boxes(screen)
		# offset = 70
		# bar_width = self.num_of_slots * offset
		# start_x = (WIDTH - bar_width)//2

		# for box in range(self.num_of_slots):
		# 	pygame.draw.rect(screen, BLACK, ((start_x + box * offset) + 10, 10, 20, 20), border_radius=2)
		# 	#self.game.render_text('000', WHITE, self.game.font, (offset - 50, 10), True)
