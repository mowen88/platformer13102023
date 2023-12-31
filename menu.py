
import random
from state import State
from scene import Scene
from dialogue import Dialogue
from settings import *

class PygameLogo(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.game = game
		self.timer = 100

		# logo
		self.logo_surf = pygame.image.load('assets/pygame_logo.png').convert_alpha()
		self.logo_rect = self.logo_surf.get_rect(center = (HALF_WIDTH, HEIGHT * 0.6))

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)
		self.intro = Intro(self.game)

	def go_to(self, state):
		self.game.play_music(self.game.track_index)
		MainMenu(self.game).enter_state()

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
		self.timer = 900

		self.text_blocks = list(INTRO_TEXT.keys())

		#dialogue
		# The strogg relentlessly assimulate all races in its path as they
		# Years have passed since the Strogg attacked Earth.
		# Their mission to relentlessly assimulate all races in their path.

		# Years have passed since the Strogg attacked earth. Harvesting many humans, augmenting themselves with the biological components of all who stand in their way.
		# Humanity launches operation overlord to counter-attack Stroggos.
		# Marine Bitterman's drop pod is knocked of course by the Strogg's planetry defences, and lands miles away from the target drop zone...

		self.text = Dialogue(self.game, ['Years have passed since the Strogg attacked, earth, harvesting humans', 'continuing to augment themselves with the biological components of all', 'who stand in their way.'], NEON_GREEN, (WIDTH * 0.075, HEIGHT * 0.2))
		self.text2 = Dialogue(self.game, ['Humanity launches operation overlord to counter-attack Stroggos.'], NEON_GREEN, (WIDTH * 0.075, HEIGHT * 0.45))
		self.text3 = Dialogue(self.game, ["Marine Bitterman's drop pod is knocked off course by the Strogg's", "planetary defences and lands miles away from the target drop zone..."], NEON_GREEN, (WIDTH * 0.075, HEIGHT * 0.7))

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)

	def go_to(self, state):
		MainMenu(self.game).enter_state()

	def update(self, dt):

		self.transition_screen.update(dt)
		self.timer -= dt

		if self.timer < 800:
			self.text.update(dt)

		if self.timer < 500:
			self.text2.update(dt)

		if self.timer < 300:
			self.text3.update(dt)

		if self.timer <= 0 or ACTIONS['space'] and self.timer < 800:
			self.next_menu = 'main_menu'
			self.transitioning = True
			self.game.reset_keys()

	def draw(self, screen):
		screen.fill(BLACK)
		self.text.draw(screen)
		self.text2.draw(screen)
		self.text3.draw(screen)
		if self.timer < 800:
			self.game.render_text('Press space to skip', WHITE, self.game.font, (HALF_WIDTH, HEIGHT * 0.95))
		self.transition_screen.draw(screen)

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

class MenuBG(pygame.sprite.Sprite):
	def __init__(self, menu):

		self.menu = menu
		self.image = pygame.Surface((random.random()*TILESIZE, random.random()*TILESIZE))
		self.image.fill(DARK_GREEN)
		self.rect = self.image.get_rect()
		self.alpha = 255

		self.speed = (random.uniform(0.1, 1.0), random.uniform(0.1, 1.0))
		self.vel = pygame.math.Vector2(self.speed)
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.pos = (random.random() * WIDTH, random.random() * HEIGHT)

	def update(self, dt):
		self.alpha = random.randrange(0, 255)
		self.pos += self.vel * dt
		self.rect.topleft = self.pos

		if self.rect.x > WIDTH:
			self.pos.x = -self.rect.width
		if self.rect.y > HEIGHT:
			self.pos.y = -self.rect.height

	def draw(self, screen):
		self.image.set_alpha(self.alpha)
		screen.blit(self.image, self.rect)

class MainMenu(State):
	def __init__(self, game):
		State.__init__(self, game)

		if len(self.game.stack) > 1:
			self.game.stack.pop()

		self.game = game
		self.alpha = 255
		self.next_menu = None
		self.padding = 24

		self.buttons = {
						'Start': [(HALF_WIDTH, HEIGHT * 0.2), 'slot_menu'],
						'Controls': [(HALF_WIDTH, HEIGHT * 0.2 + self.padding), 'controls_menu'],
						'Quit': [(HALF_WIDTH, HEIGHT * 0.2 + self.padding * 2), 'quit_game'],
						}

		# menu transitioning
		self.transitioning = False
		self.transition_screen = MenuTransition(self)
		self.boxes = self.get_boxes()

		self.scene = Scene(self.game, SCENE_DATA[SAVE_DATA['current_scene']]['level'], SAVE_DATA['current_scene'], SAVE_DATA['entry_pos'])

		self.logo_surf = pygame.image.load('assets/quake_logo.png').convert_alpha()
		self.logo_rect = self.logo_surf.get_rect(center = RES/2)

	def get_boxes(self):
		boxes = []
		for x in range(int(RES.magnitude()//2)):
			boxes.append(MenuBG(self))
		return boxes

	def render_button(self, screen, current_menu, next_menu, text_colour, button_colour, hover_colour, pos):
		mx, my = pygame.mouse.get_pos()

		colour = text_colour

		surf = self.game.font.render(current_menu, False, colour)
		rect = pygame.Rect(0,0, surf.get_width() + 16, surf.get_height() * 2)
		rect.center = pos

		if rect.collidepoint(mx, my) and not self.transitioning:
			pygame.draw.rect(screen, hover_colour, rect, 1)#int(HEIGHT * 0.05))
			pygame.draw.line(screen, NEON_GREEN, rect.midleft, (0, rect.centery), 1)
			pygame.draw.line(screen, NEON_GREEN, rect.midright, (WIDTH, rect.centery), 1)
			self.game.render_text(current_menu, text_colour, self.game.font, pos)
			if ACTIONS['left_click']:
				self.next_menu = next_menu
				self.game.item_fx['menu'].play()
		else:
			#pygame.draw.rect(screen, button_colour, rect)#int(HEIGHT * 0.05))
			self.game.render_text(current_menu, text_colour, self.game.font, pos)

	def go_to(self, state):
		if state == 'quit_game':
			self.game.running = False

		elif state == 'main_menu':
			MainMenu(self.game).enter_state()
		elif state == 'controls_menu':
			ControlsMenu(self.game).enter_state()
		elif state == 'slot_menu':
			SlotMenu(self.game).enter_state()
		elif state == 'options_menu':
			SlotMenu(self.game).enter_state()
		elif state == 'DELETE_SLOT':
			AreYouSureMenu(self.game).enter_state()
		elif state == 'delete_confirmed':
			Confirmation(self.game).enter_state()
		elif state in list(self.game.slot_data.keys()):
			StartGameMenu(self.game).enter_state()
 
		else:
			self.game.stop_music()
			self.scene.enter_state()

	def update(self, dt):

		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

		screen.blit(self.logo_surf, self.logo_rect)
		self.game.render_text('a fan game by Matt Owen', WHITE, self.game.font, (WIDTH * 0.82, HEIGHT * 0.95))

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.transition_screen.draw(screen)

class ControlsMenu(MainMenu):
	def __init__(self, game):
		super().__init__(game)

		self.controls_image = pygame.image.load('assets/controls.png').convert_alpha()
		self.controls_rect = self.controls_image.get_rect(center = RES/2)

		self.buttons = {'Back': [(HALF_WIDTH, HEIGHT * 0.9), 'main_menu']}

	def update(self, dt):
	
		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

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
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.transition_screen.draw(screen)	

class SlotMenu(MainMenu):
	def __init__(self, game):
		super().__init__(game)

		self.num_of_slots = len(list(self.game.slot_data.keys()))
		self.buttons = self.get_slots()

	def get_slots(self):
		buttons = {}
		for slot in range(1, self.num_of_slots+1):
			start_y = HALF_HEIGHT - self.num_of_slots * 0.5 * self.padding

			percent_complete = f"{int(len(self.game.read_slot_progress(slot, 'scenes_completed'))/self.game.max_num_of_scenes * 100)} %"

			buttons.update({f'save {slot}' + ' -- ' + str(self.game.read_slot_progress(slot, 'level')) +' -- '+ str(self.game.read_slot_progress(slot, 'time_elapsed'))\
			+' -- '+ str(percent_complete) :[(HALF_WIDTH, start_y + self.padding * (slot-1)), str(slot)]})
		
		buttons.update({'Back': [(HALF_WIDTH, start_y + 8 + self.padding * self.num_of_slots), 'main_menu']})
		return buttons

	def activate_slot(self):
		self.game.slot = self.next_menu
		if self.next_menu in list(self.game.slot_data.keys()):
			self.game.slot = str(self.next_menu)

			self.game.read_data()
			#self.game.read_data()

	def update(self, dt):
	
		for box in self.boxes:
			box.update(dt)

		self.activate_slot()

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

		self.game.render_text('Select Slot', WHITE, self.game.font, (HALF_WIDTH, HEIGHT * 0.15))

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.transition_screen.draw(screen)	

class AreYouSureMenu(MainMenu):
	def __init__(self, game):
		super().__init__(game)

		self.buttons = {
				'Confirm': [(HALF_WIDTH, HALF_HEIGHT), 'delete_confirmed'],
				'Back': [(HALF_WIDTH, HALF_HEIGHT + self.padding), 'slot_menu']
				}

	def update(self, dt):

		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)
		
		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.game.render_text(f"Delete slot {self.game.slot} data?", WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding * 1.5))

		self.transition_screen.draw(screen)

class Confirmation(MainMenu):
	def __init__(self, game):
		super().__init__(game)

		self.delete_data()

		self.buttons = {
				'Continue': [(HALF_WIDTH, HALF_HEIGHT + self.padding * 0.5), 'slot_menu']
				}

	def delete_data(self):
		COMMIT_SAVE_DATA.update({
		'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 0, 'ammo_capacity':'normal',
		'armour_type':'normal', 'armour':0, 'max_armour':0, 'shards': 0, 'stimpacks': 0, 'health':100, 'max_health':100,
		'items':[], 'guns_collected':['blaster', 'hand grenade'],
		'keys_collected':[], 'killed_sprites':[], 'scenes_completed':[], 'time_elapsed': "00:00:00"
		})
		# 'time': "00:00:00"})
		COMMIT_AMMO_DATA.update({'infinite': 0, 'cells':0, 'shells':0, 'bullets':0,
		'grenades':5, 'slugs':0, 'rockets':0})
		self.game.write_data()

	def update(self, dt):

		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.transitioning = True

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

		# slot deleted confirmation message
		self.game.render_text(f"Slot {self.game.slot} deleted!", WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding))
		
		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.transition_screen.draw(screen)

class StartGameMenu(MainMenu):
	def __init__(self, game):
		super().__init__(game)

		self.buttons = {
				'Continue': [(HALF_WIDTH, HALF_HEIGHT + self.padding * 0.5), 'GO!!!'],
				'Delete Data': [(HALF_WIDTH, HALF_HEIGHT + self.padding * 1.5), 'DELETE_SLOT'],
				'Back': [(HALF_WIDTH, HALF_HEIGHT + self.padding * 2.5), 'slot_menu']
				}

	def show_stats(self):
		if self.game.slot is not None:
			self.game.render_text(f"save {self.game.slot}" +" -- "+ str(self.game.read_slot_progress(self.game.slot, 'unit')) +" -- "+ str(self.game.read_slot_progress(self.game.slot, 'level')), WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding * 3))
			self.game.render_text(SAVE_DATA['time_elapsed'], WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding * 2))
			self.game.render_text(self.game.slot_data[self.game.slot]['percent_complete'], WHITE, self.game.font, (HALF_WIDTH, HALF_HEIGHT - self.padding))
			

	def start_timer(self):
		if self.next_menu == 'GO!!!':
			self.game.timer.stop_start()

	def update(self, dt):

		for box in self.boxes:
			box.update(dt)

		self.transition_screen.update(dt)
		if self.next_menu is not None:
			self.start_timer()
			self.transitioning = True

		# print(self.game.slot)

	def draw(self, screen):
		screen.fill(BLACK)

		for box in self.boxes:
			box.draw(screen)

		for name, values in self.buttons.items():
			self.render_button(screen, name, values[1], NEON_GREEN, BLACK, NEON_GREEN, values[0])

		self.show_stats()

		self.transition_screen.draw(screen)