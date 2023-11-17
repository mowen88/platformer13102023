import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,225)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)

HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False, 'left':False, 'right':False,
			'left_click':False, 'right_click':False, 'scroll_up':False, 'scroll_down':False}

LAYERS = {'blocks':0,
		  'player':1,
		  'particles':2,
		  'foreground':3}

FONT = 'fonts/homespun.ttf'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (212, 30, 60)
NEON_BLUE = (120, 215, 225)
NEON_GREEN = (61, 255, 110)
YELLOW = (255, 255, 64)
BROWN = (110, 74, 57)
LIGHT_GREY = (199, 212, 225)

SCENE_DATA = {
			'0':{'1':'1'},
			'1':{'1':'0'}
			}

SAVE_DATA = {'current_scene':'0', 'entry_pos':'0', 'armour_type':'Body', 'armour':100, 'max_armour':100, 'health':100, 'max_health':100}

DATA = {
	'player':{'current_scene':0, 'entry_pos':0, 'armour_type':'Body', 'armour':100, 'max_armour':100, 'health':100, 'max_health':100},

	'guns':{
			'blaster': {'ammo_type': 'cells', 'cooldown': 30, 'speed': 4, 'damage': 3, 'path': '../assets/weapons/blaster.png', 'length':18, 'auto':False},
			'shotgun': {'ammo_type': 'shells', 'cooldown': 80, 'speed': 0, 'damage': 4, 'path': '../assets/weapons/shotgun.png', 'length':25, 'auto':False},
			'grenade': {'ammo_type': 'grenade','cooldown': 180, 'speed': 0, 'damage': 20, 'path': '../assets/weapons/grenade.png', 'length':15, 'auto':False},
			'machine gun': {'ammo_type': 'bullets', 'cooldown': 8, 'speed': 0, 'damage': 2, 'path': '../assets/weapons/machine gun.png', 'length':20, 'auto':True},
			'super shotgun': {'ammo_type': 'shells','cooldown': 80, 'speed': 0, 'damage': 6, 'path': '../assets/weapons/super shotgun.png', 'length':25, 'auto':False},
			'chain gun': {'ammo_type': 'bullets', 'cooldown': 10, 'speed': 0, 'damage': 4, 'path': '../assets/weapons/chain gun.png', 'length':22, 'auto':True},
			'grenade launcher': {'ammo_type': 'grenade', 'cooldown': 50, 'speed': 0, 'damage': 50, 'path': '../assets/weapons/grenade launcher.png', 'length':15, 'auto':False},
			'rocket launcher': {'ammo_type': 'rockets', 'cooldown': 50, 'speed': 2, 'damage': 400, 'path': '../assets/weapons/rocket launcher.png', 'length':20, 'auto':False},
			'railgun': {'ammo_type': 'slugs', 'cooldown': 120, 'speed': 0, 'damage': 50, 'path': '../assets/weapons/railgun.png', 'length':20, 'auto':False},
			'hyper blaster': {'ammo_type': 'cells', 'cooldown': 1, 'speed': 5, 'damage': 50, 'path': '../assets/weapons/hyper_blaster.png', 'length':20, 'auto':True},
			'BFG': {'ammo_type': 'cells', 'cooldown': 200, 'speed': 4, 'damage': 100, 'path': '../assets/weapons/BFG.png', 'length':20, 'auto':False},
			},
	'enemies' :{
			'guard':{'weapon': 'blaster', 'damage': 5, 'health': 30, 'telegraph_time': 25, 'cooldown': 60, 'burst_count': 3},
			'sg_guard': {'weapon':'machine gun', 'damage': 4, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'mg_guard': {'weapon':'machine gun', 'damage': 5, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'gladiator': {'weapon':'railgun', 'damage': 60, 'health': 40, 'telegraph_time': 25, 'cooldown': 30, 'burst_count': 3},
			},

	'abilities':{
			'double_jump': True,
			'dash': False,
			'wall_jump': False,
			'hover': False,
			'ground_smash': False,
			},
		}