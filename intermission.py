import pygame, math
from state import State
from settings import *
from timer import Timer
from dialogue import Dialogue

class Block(pygame.sprite.Sprite):
	def __init__(self, pos, name):
		self.image = pygame.Surface((TILESIZE//2, TILESIZE//2))
		self.image.fill(NEON_GREEN)
		self.rect = self.image.get_rect(center = pos)
		self.name = name

class Intermission(State):
	def __init__(self, game, scene, new_scene):
		State.__init__(self, game)

		if len(self.game.stack) > 1:
			self.game.stack.pop()
			
		self.time_elapsed = COMMIT_SAVE_DATA['time_elapsed']

		self.game = game
		self.scene = scene
		self.new_scene = new_scene #new_scene
		self.new_level = SCENE_DATA[self.scene.new_scene]["level"]
		self.new_unit = SCENE_DATA[self.scene.new_scene]["unit"]
		self.prev_unit = SCENE_DATA[self.scene.current_scene]['unit']
		
		#self.units = {'base':(20, 200), 'bunker':(80, 150), 'jail':(120, 150), 'unit 3':(220, 120), 'unit 4':(300, 100), 'unit 6':(350, 80), 'unit 7':(380, 40)}
		self.units = {'unit 1':(20, 200), 'unit 2':(80, 150), 'jail':(120, 150), 'base':(220, 120), 'bunker':(300, 100), 'unit 6':(350, 80), 'unit 7':(380, 40)}

		self.line_blinker_timer = Timer(20, 5, 10)
		self.line_blinker_timer.start()

		self.acquiring_text = Dialogue(self.game, ['Acquiring.....'], NEON_GREEN, (WIDTH * 0.1, HEIGHT * 0.1))
		self.exiting_text = Dialogue(self.game, [f'Exiting the {self.prev_unit} area.....'], NEON_GREEN, (WIDTH * 0.1 + TILESIZE, HEIGHT * 0.2))
		self.entering_text = Dialogue(self.game, [f'Proceeding to the,',f'{self.new_unit} area.....'], NEON_GREEN, (WIDTH * 0.6, HEIGHT * 0.8))

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

	def draw_mission_blocks(self, points, screen):
		for unit, pos in self.units.items():
			if pos in points:
				block = Block(pos, unit)
				screen.blit(block.image, block.rect)
				pygame.draw.rect(screen, BLACK, (block.rect.x +2, block.rect.y +2, block.rect.width -4, block.rect.height -4))

	def draw_lines(self, screen):
		points = []
		unit_keys = list(self.units.keys())
		for unit in unit_keys:
			pos = self.units[unit]

			if unit_keys.index(unit) <= unit_keys.index(self.new_unit):
				points.append(pos)

		if len(points) > 1:
			pygame.draw.lines(screen, NEON_GREEN, False, points[:-1], 2)
			self.draw_mission_blocks(points[:-1], screen)

		if not self.line_blinker_timer.var:
			pygame.draw.line(screen, WHITE, self.units[self.new_unit], self.units[self.prev_unit], 2)
			self.draw_mission_blocks(points, screen)
			self.draw_time_spent(screen)

	def draw_time_spent(self, screen):
		self.game.render_text('Time elapsed:', NEON_GREEN, self.game.ui_font, (WIDTH * 0.8, TILESIZE))
		self.game.render_text(self.time_elapsed, NEON_GREEN, self.game.ui_font, (WIDTH * 0.8, TILESIZE *2))

	def text_interval_logic(self, dt):
		self.acquiring_text.update(dt)
		if self.acquiring_text.done:
			self.timer -= dt
			if self.timer <= 400:
				self.exiting_text.update(dt)
		if self.exiting_text.done:
			self.line_blinker_timer.update(dt)
		if not self.line_blinker_timer.running:
			self.entering_text.update(dt)
			if self.timer <= 0:
				self.opening = False

	def text_interval_draw(self, screen):
		self.acquiring_text.draw(screen)
		if self.timer <= 400:
			self.exiting_text.draw(screen)
			pygame.draw.rect(screen, NEON_GREEN, (self.exiting_text.pos[0] - TILESIZE - 2, self.exiting_text.pos[1] -2, TILESIZE//2, TILESIZE//2), 2)
		if not self.line_blinker_timer.running:
			self.entering_text.draw(screen)
			pygame.draw.rect(screen, NEON_GREEN, (self.entering_text.pos[0] - TILESIZE - 2, self.entering_text.pos[1] -TILESIZE//2, TILESIZE//2, TILESIZE//2), 2)

	def update(self, dt):

		self.text_interval_logic(dt)
		self.blackbar_logic(dt)


	def draw(self, screen):
		screen.fill(DARK_GREEN)
		self.text_interval_draw(screen)
		self.draw_lines(screen)
		self.draw_blackbars(screen)
		
		
	