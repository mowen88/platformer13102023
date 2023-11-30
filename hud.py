import pygame
from settings import *

class HUD:
	def __init__(self, game, scene):

		self.game = game
		self.scene = scene
		self.data = ['health','armour','ammo']
		self.num_of_slots = len(self.data)

	def alpha_rect(self, screen, colour, rect):
		surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
		pygame.draw.rect(surf, colour, surf.get_rect())
		screen.blit(surf, rect)

	def draw_boxes(self, screen):
		
		offset = 70
		max_width = self.num_of_slots * offset
		start_x = (WIDTH - max_width)//2

		for box in range(self.num_of_slots):
			if (box == 1 and SAVE_DATA['armour_type'] == 'normal') or (box == 2 and self.scene.player.gun == 'blaster'):
				continue

			icon = pygame.image.load(f'assets/icons/{box}.png').convert_alpha()
			rect = self.alpha_rect(screen, (0, 0, 0, 127), (start_x + box * offset, 16, 53, 20))
			screen.blit(icon, (start_x + box * offset, 16))
			
			#change colour of health to red if under 25 health
			colour = RED if box == 0 and SAVE_DATA[self.data[box]] < 25 else WHITE
			self.game.render_text(int(SAVE_DATA[self.data[box]]), colour, self.game.font, (start_x + 26 + box * offset, 16), True)

	def update(self, dt):
		pass

	def draw(self, screen):
		self.draw_boxes(screen)