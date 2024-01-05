
import pygame, math
from state import State
from settings import *

class DemoEnd(State):
	def __init__(self, game, scene, new_scene):
		State.__init__(self, game)

		self.scene = scene
		self.new_scene = new_scene
		self.time_elapsed = COMMIT_SAVE_DATA['time_elapsed']

		self.timer = 500
		self.opening = True
		self.bar_count = 10
		self.bar_width = WIDTH//self.bar_count
		self.bar_height = HEIGHT//self.bar_count
		self.blackbar = pygame.Surface((self.bar_width, self.bar_height))

	def blackbar_logic(self, dt):

		target_width = WIDTH/(self.bar_count // 9 * 16) if not self.opening else 0
		target_height = HEIGHT/self.bar_count if not self.opening else 0

		self.bar_width += ((target_width - self.bar_width) / 10) * dt
		self.bar_height += ((target_height - self.bar_height) / 10) * dt

		if (self.bar_height >= target_height and not self.opening) or (self.bar_height <= target_height and self.opening):
			self.bar_height = target_height
			self.opening = not self.opening

		if not self.opening and self.bar_height >= target_height -1:
			self.scene.create_scene(self.scene.prev_level, self.new_scene)

	def draw_blackbars(self, screen):
		for x in range(self.bar_count // 9 * 16):
			for y in range(self.bar_count):
				pygame.draw.rect(screen, BLACK, (x * WIDTH/(self.bar_count // 9 * 16), y * HEIGHT/self.bar_count, self.bar_width, self.bar_height))

	def update(self, dt):


		if ACTIONS['space']:
			self.opening = False
			# timer reset and stop 
			# self.game.timer.stop_start()
			# self.game.timer.reset()
			# self.game.write_game_time()

			# self.exit_state()
			# self.prev_state.exit_state()
			self.game.reset_keys()

		self.blackbar_logic(dt)

	def draw(self, screen):
		screen.fill(BLACK)
		self.game.render_text('Thanks for playing this demo !', WHITE, self.game.ui_font, (WIDTH * 0.5, HEIGHT * 0.4))
		self.game.render_text('Completion time', NEON_GREEN, self.game.font, (WIDTH * 0.5, HEIGHT * 0.55))
		self.game.render_text(str(self.time_elapsed), NEON_GREEN, self.game.font, (WIDTH * 0.5, HEIGHT * 0.6))

		self.draw_blackbars(screen)