
import pygame, math
from state import State
from settings import *

class DemoEnd(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.time_elapsed = COMMIT_SAVE_DATA['time_elapsed']

	def update(self, dt):

		if ACTIONS['enter']:
			# timer reset and stop 
			self.game.timer.stop_start()
			self.game.timer.reset()
			self.game.write_game_time()

			self.exit_state()
			self.prev_state.exit_state()
			self.game.reset_keys()

	def draw(self, screen):
		screen.fill(BLACK)
		self.game.render_text('Thanks for playing this demo !', WHITE, self.game.ui_font, (WIDTH * 0.5, HEIGHT * 0.4))
		self.game.render_text('Completion time', NEON_GREEN, self.game.font, (WIDTH * 0.5, HEIGHT * 0.55))
		self.game.render_text(str(self.time_elapsed), NEON_GREEN, self.game.font, (WIDTH * 0.5, HEIGHT * 0.6))