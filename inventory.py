from state import State
from settings import *

class Inventory(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.activated = None
		self.padding = 24

		self.buttons = self.get_list()
		self.fade_surf = pygame.Surface((RES))
		self.fade_surf.fill(BLACK)

	def get_list(self):
		buttons = {}
		for num, item in enumerate(SAVE_DATA['items']):
			pos = (HALF_WIDTH, HALF_HEIGHT - self.padding//2 + self.padding * num)
			buttons.update({item:[pos, item]})
		return buttons

	def show_title(self, title_name, colour):
		pos = (HALF_WIDTH, HALF_HEIGHT - self.padding * 2)
		self.game.render_text(title_name, colour, self.game.font, pos)

	def render_button(self, screen, current_menu, activated, text_colour, button_colour, hover_colour, pos):
		mx, my = pygame.mouse.get_pos()

		colour = text_colour

		surf = self.game.font.render(current_menu, False, colour)
		rect = pygame.Rect(0,0, HALF_WIDTH - 60, surf.get_height() * 1.5)
		rect.center = pos

		if rect.collidepoint(mx, my):
			pygame.draw.rect(screen, hover_colour, rect, 2)#int(HEIGHT * 0.05))
			pygame.draw.line(screen, NEON_GREEN, rect.midleft, (0, rect.centery))
			pygame.draw.line(screen, NEON_GREEN, rect.midright, (WIDTH, rect.centery))
			self.game.render_text(current_menu, text_colour, self.game.font, pos)
			if ACTIONS['left_click']:
				self.activated = activated
		else:
			#pygame.draw.rect(screen, button_colour, rect)#int(HEIGHT * 0.05))
			self.game.render_text(current_menu, text_colour, self.game.font, pos)


	def update(self, dt):
		if ACTIONS['enter']:
			self.activated = None 
			self.exit_state()
			self.game.reset_keys()

		elif self.activated == 'quad damage':
			self.activated = None 
			#self.game.quit_write_data()
			self.exit_state()
			self.game.reset_keys()

	def draw(self, screen):
		self.prev_state.draw(screen)

		self.fade_surf.set_alpha(180)
		screen.blit(self.fade_surf, (0,0))

		self.show_title('Inventory', WHITE)

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, NEON_GREEN, NEON_GREEN, values[0])

		#self.draw_bounding_box(screen)



