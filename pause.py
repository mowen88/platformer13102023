from state import State
from settings import *

class PauseMenu(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.next_menu = None
		self.padding = 16
		self.controls_screen = ControlsScreen(self.game)

		self.buttons = {
						'continue': [(HALF_WIDTH, HALF_HEIGHT - self.padding), 'unpause'],
						'controls': [(HALF_WIDTH, HALF_HEIGHT), 'controls'],
						'quit to menu': [(HALF_WIDTH, HALF_HEIGHT + self.padding), 'main_menu']
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
				self.game.item_fx['menu'].play()
				self.next_menu = next_menu
		else:
			self.game.render_text(current_menu, text_colour, self.game.font, pos)

	def update(self, dt):
		if ACTIONS['space'] or self.next_menu == 'unpause':
			self.next_menu = None 
			self.exit_state()
			self.game.reset_keys()

		elif self.next_menu == 'controls':
			self.controls_screen.enter_state()
			self.next_menu = None

		elif self.next_menu == 'main_menu':
			self.game.stop_music()
			self.game.play_music(0)
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

		self.game.render_text('Paused', WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding * 2.5))

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, NEON_GREEN, NEON_GREEN, values[0])

class ControlsScreen(PauseMenu):
	def __init__(self, game):
		State.__init__(self, game)

		self.next_menu = None

		self.controls_image = pygame.image.load('assets/controls.png').convert_alpha()
		self.controls_rect = self.controls_image.get_rect(center = RES/2)

		self.buttons = {'back': [(HALF_WIDTH, HEIGHT * 0.9), 'back']}

		self.fade_surf = pygame.Surface((RES))
		self.fade_surf.fill(BLACK)

	def update(self, dt):
		if self.next_menu == 'back':
			self.exit_state()
			self.next_menu = None
			
	def draw(self, screen):
		self.prev_state.prev_state.draw(screen)

		self.fade_surf.set_alpha(180)
		screen.blit(self.fade_surf, (0,0))
		
		screen.blit(self.controls_image, self.controls_rect)
		self.game.render_text('Controls', WHITE, self.game.font, (HALF_WIDTH, HEIGHT * 0.1))

		self.game.render_text('shoot', WHITE, self.game.font, (60,48), True)
		self.game.render_text('mouse to aim', WHITE, self.game.font, (60,60), True)
		self.game.render_text('jump', WHITE, self.game.font, (70,150), True)
		self.game.render_text('change weapon', WHITE, self.game.font, (70,164), True)
		self.game.render_text('pause', WHITE, self.game.font, (128,150), True)
		self.game.render_text('inventory', WHITE, self.game.font, (164,150), True)
		self.game.render_text('enter door /', WHITE, self.game.font, (284,45), True)
		self.game.render_text('climb ladder', WHITE, self.game.font, (284,55), True)
		self.game.render_text('move right', WHITE, self.game.font, (284,130), True)
		self.game.render_text('crouch / descend ladder', WHITE, self.game.font, (284,150), True)
		self.game.render_text('move left', WHITE, self.game.font, (284,170), True)

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, NEON_GREEN, NEON_GREEN, values[0])