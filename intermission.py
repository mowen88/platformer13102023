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

		self.game.write_game_time()

		self.game = game
		self.scene = scene
		self.new_scene = new_scene #new_scene
		self.new_level = SCENE_DATA[self.scene.new_scene]["level"]
		self.new_unit = SCENE_DATA[self.scene.new_scene]["unit"]
		self.prev_unit = SCENE_DATA[self.scene.current_scene]['unit']
		
		self.units = {'base':(20, 200), 'bunker':(80, 150), 'jail':(120, 150), 'unit 3':(220, 120), 'unit 4':(300, 100), 'unit 6':(350, 80), 'unit 7':(380, 40)}
		#self.units = {'unit 1':(20, 200), 'unit 2':(80, 150), 'jail':(120, 150), 'base':(220, 120), 'bunker':(300, 100), 'unit 6':(350, 80), 'unit 7':(380, 40)}

		self.text = ['[ You are entering', f'the {self.new_unit} ]']

		self.line_blinker_timer = Timer(20, 5, 10)
		self.line_blinker_timer.start()
		self.dialogue =Dialogue(self.game, self.scene, self.text, NEON_GREEN)

	def draw_mission_blocks(self, points, current_pos, screen):
		for unit, pos in self.units.items():
			if pos in points or pos == current_pos:
				block = Block(pos, unit)
				screen.blit(block.image, block.rect)
				pygame.draw.rect(screen, BLACK, (block.rect.x +2, block.rect.y +2, block.rect.width -4, block.rect.height -4))

	def draw_lines(self, screen):
		points = []
		unit_keys = list(self.units.keys())
		for unit in unit_keys:
			pos = self.units[unit]

			if unit_keys.index(unit) < unit_keys.index(self.new_unit):
				points.append(pos)

		if len(points) > 1:
			pygame.draw.lines(screen, NEON_GREEN, False, points, 2)

		if not self.line_blinker_timer.var:
			pygame.draw.line(screen, WHITE, self.units[self.new_unit], self.units[self.prev_unit], 2)

		self.draw_mission_blocks(points, self.units[self.new_unit], screen)

	def draw_time_spent(self, screen):
		self.game.render_text('Time elapsed:', NEON_GREEN, self.game.ui_font, (HALF_WIDTH, TILESIZE))
		self.game.render_text(SAVE_DATA['time_elapsed'], NEON_GREEN, self.game.ui_font, (HALF_WIDTH, TILESIZE *2))

	def update(self, dt):

		# logic to return to menu
		if ACTIONS['enter']:
			self.exit_state()
			#self.scene.create_scene(self.scene.prev_level, self.new_scene)
			ACTIONS['enter'] = False

		self.line_blinker_timer.update(dt)

		if not self.line_blinker_timer.running:
			self.dialogue.update(dt)

	def draw(self, screen):
		screen.fill(DARK_GREEN)

		if not self.line_blinker_timer.running:
			self.dialogue.draw(screen)

		self.draw_time_spent(screen)

		self.draw_lines(screen)
		
		# end of demo temp text
		self.game.render_text('End of Demo', WHITE, self.game.ui_font, RES/2)
	