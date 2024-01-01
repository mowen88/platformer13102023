import random
from state import State
from dialogue import Dialogue
from settings import *

class MenuTransition(pygame.sprite.Sprite):
	def __init__(self, menu):

		self.menu = menu
		self.surf = pygame.Surface((RES))
		self.surf.fill(WHITE)
		self.alpha = 255
		self.timer = RES * 0.1
		self.fade_in_duration = 30
		self.fade_out_duration = 10

	def update(self, dt):

		if not self.menu.transitioning:
			self.alpha -= self.fade_in_duration * dt
			if self.alpha <= 0: 
				self.alpha = 0
		else:
			self.alpha += self.fade_out_duration * dt
			if self.alpha >= 255:
				self.menu.go_to(self.menu.next_menu)

	def draw(self, screen):
		self.surf.set_alpha(self.alpha)
		screen.blit(self.surf, (0,0))

class PygameLogo(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.game = game
		self.timer = 50

		# logo
		self.logo_surf = pygame.image.load('assets/pygame_logo.png').convert_alpha()
		self.logo_rect = self.logo_surf.get_rect(center = (HALF_WIDTH, HEIGHT * 0.6))

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)

	def go_to(self, state):
		Intro(self.game).enter_state()

	def update(self, dt):
		# if ACTIONS['space']:
		# 	Scene(self.game).enter_state()
		# 	ACTIONS['space'] = False

		self.transition_screen.update(dt)

		self.timer -= dt
		if self.timer <= 0:
			self.next_menu = 'main_menu'
			self.transitioning = True
			self.game.reset_keys()

	def draw(self, screen):
		screen.fill(WHITE)
		screen.blit(self.logo_surf, self.logo_rect)
		self.game.render_text('Made with', BLACK, self.game.font, (HALF_WIDTH, HEIGHT * 0.3))
		self.transition_screen.draw(screen)

class Intro(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.game = game
		self.timer = 300

		#dialogue
		self.text = Dialogue(self.game, ['Intro and a load more waffle', 'that has something to do', 'with the story....'], NEON_GREEN, (WIDTH * 0.1, HEIGHT * 0.1))

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)

	def go_to(self, state):
		MainMenu(self.game).enter_state()

	def update(self, dt):
		# if ACTIONS['space']:
		# 	Scene(self.game).enter_state()
		# 	ACTIONS['space'] = False

		self.transition_screen.update(dt)
		self.timer -= dt

		if self.timer < 200:
			self.text.update(dt)

		if self.timer <= 0:
			self.next_menu = 'main_menu'
			self.transitioning = True
			self.game.reset_keys()

	def draw(self, screen):
		screen.fill(DARK_GREEN)
		self.text.draw(screen)
		self.transition_screen.draw(screen)
