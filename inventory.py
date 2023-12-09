from state import State
from settings import *

class Inventory(State):
	def __init__(self, game, scene):
		State.__init__(self, game)

		self.scene = scene
		self.activated_item = None
		self.padding = 24

		self.no_items_message = 'No items collected. Get back to work !'
		self.buttons = self.get_list()
		self.fade_surf = pygame.Surface((RES))
		self.fade_surf.fill(BLACK)

	def get_list(self):
		buttons = {}

		for num, item in enumerate(SAVE_DATA['items']):
			pos = (HALF_WIDTH, HALF_HEIGHT - self.padding * 1.5 + self.padding * num)
			buttons.update({item:[pos, item]})
		
		if not SAVE_DATA['items']:
			no_item_msg_pos = (HALF_WIDTH, HALF_HEIGHT - self.padding + self.padding * len(SAVE_DATA['items']))
			buttons.update({self.no_items_message: [no_item_msg_pos, 'exit']})
			back_pos = (HALF_WIDTH, HALF_HEIGHT - self.padding + self.padding * 1.5)
		else:
			# Add the 'back' button at the end of the list
			back_pos = (HALF_WIDTH, HALF_HEIGHT - self.padding + self.padding * len(SAVE_DATA['items']))
		buttons.update({'exit': [back_pos, 'exit']})

		return buttons

	def show_title(self, title_name, colour):
		pos = (HALF_WIDTH, HALF_HEIGHT - self.padding * 3)
		self.game.render_text(title_name, colour, self.game.font, pos)


	def render_button(self, screen, hovered_item, activated_item, text_colour, button_colour, hover_colour, pos):
		mx, my = pygame.mouse.get_pos()

		colour = text_colour

		surf = self.game.font.render(hovered_item, False, colour)
		rect = pygame.Rect(0,0, HALF_WIDTH - 60, surf.get_height() * 1.5)
		rect.center = pos

		if rect.collidepoint(mx, my) and hovered_item != self.no_items_message:
			pygame.draw.rect(screen, hover_colour, rect, 1)
			pygame.draw.line(screen, NEON_GREEN, rect.midleft, (0, rect.centery))
			pygame.draw.line(screen, NEON_GREEN, rect.midright, (WIDTH, rect.centery))
			self.game.render_text(hovered_item, text_colour, self.game.font, pos)
			if ACTIONS['left_click']:
				self.activated_item = activated_item
		else:
			self.game.render_text(hovered_item, text_colour, self.game.font, pos)


	def update(self, dt):
		if ACTIONS['enter'] or self.activated_item == 'exit':
			self.activated_item = None 
			self.exit_state()
			self.game.reset_keys()

		elif self.activated_item in SAVE_DATA['items']:

			if self.activated_item == 'quad damage' and not self.scene.player.quad_damage:
				self.scene.quad_timer.start()
				SAVE_DATA['items'].remove(self.activated_item)

			if self.activated_item == 'invulnerability' and not self.scene.player.invulnerable:
				self.scene.invulnerability_timer.start()
				SAVE_DATA['items'].remove(self.activated_item)

			if self.activated_item == 'rebreather' and not self.scene.player.rebreather:
				self.scene.rebreather_timer.start()
				SAVE_DATA['items'].remove(self.activated_item)

			if self.activated_item == 'envirosuit' and not self.scene.player.envirosuit:
				self.scene.envirosuit_timer.start()
				SAVE_DATA['items'].remove(self.activated_item)

			if self.activated_item == 'adrenaline':
				current_max = SAVE_DATA['max_health']
				SAVE_DATA.update({'max_health':current_max + 1})
				SAVE_DATA.update({'health':SAVE_DATA['max_health']})
				SAVE_DATA['items'].remove(self.activated_item)

			self.buttons = self.get_list()
			self.activated_item = None 
			self.exit_state()
			self.game.reset_keys()


	def draw(self, screen):
		self.prev_state.draw(screen)

		self.fade_surf.set_alpha(180)
		screen.blit(self.fade_surf, (0,0))

		self.show_title('Inventory', WHITE)

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, NEON_GREEN, NEON_GREEN, values[0])



