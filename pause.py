from state import State
from settings import *

class PauseMenu(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.next_menu = None
		self.padding = 24

		self.buttons = {
						'Continue': [(HALF_WIDTH, HALF_HEIGHT), 'unpause'],
						'Quit to Menu': [(HALF_WIDTH, HALF_HEIGHT + self.padding), 'main_menu']
						}
		self.fade_surf = pygame.Surface((RES))
		self.fade_surf.fill(BLACK)

	def render_button(self, screen, current_menu, next_menu, text_colour, button_colour, hover_colour, pos):
		mx, my = pygame.mouse.get_pos()

		colour = text_colour

		surf = self.game.font.render(current_menu, False, colour)
		rect = pygame.Rect(0,0, HALF_WIDTH - 60, surf.get_height() * 1.5)
		rect.center = pos

		if rect.collidepoint(mx, my):
			pygame.draw.rect(screen, hover_colour, rect, 1)
			pygame.draw.line(screen, NEON_GREEN, rect.midleft, (0, rect.centery))
			pygame.draw.line(screen, NEON_GREEN, rect.midright, (WIDTH, rect.centery))
			self.game.render_text(current_menu, text_colour, self.game.font, pos)
			if ACTIONS['left_click']:
				self.next_menu = next_menu
		else:
			self.game.render_text(current_menu, text_colour, self.game.font, pos)

	def update(self, dt):
		if ACTIONS['space'] or self.next_menu == 'unpause':
			self.next_menu = None 
			self.exit_state()
			self.game.reset_keys()

		elif self.next_menu == 'main_menu':
			self.next_menu = None

			# timer reset and stop 
			self.game.timer.stop_start()
			self.game.timer.reset()
			self.game.write_game_time()

			self.exit_state()
			self.prev_state.exit_state()
			self.prev_state.prev_state.exit_state()
			self.game.reset_keys()

	def draw(self, screen):
		self.prev_state.draw(screen)

		self.fade_surf.set_alpha(180)
		screen.blit(self.fade_surf, (0,0))

		self.game.render_text('Paused', WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding * 1.5))

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, NEON_GREEN, NEON_GREEN, values[0])
