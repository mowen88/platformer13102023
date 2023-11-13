import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,225)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)

HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False, 'left':False, 'right':False,
			'left_click':False, 'right_click':False, 'scroll_up':False, 'scroll_down':False}

LAYERS = {'blocks':0,
		  'player':1,
		  'particles':2}

FONT = 'fonts/homespun.ttf'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 100, 100)
NEON_BLUE = (176, 255, 241)
YELLOW = (255, 255, 64)
BROWN = (110, 74, 57)
LIGHT_GREY = (199, 212, 225)

DATA = {

	'guns':{
			'blaster': {'ammo_type': None, 'bullet_type': 'projectile', 'cooldown': 30, 'speed': 4, 'damage': 3, 'path': '../assets/weapons/blaster.png', 'length':18, 'auto':False},
			'shotgun': {'ammo_type': 'shells', 'bullet_type': 'bullet', 'cooldown': 80, 'speed': 0, 'damage': 4, 'path': '../assets/weapons/shotgun.png', 'length':25, 'auto':False},
			'grenade': {'ammo_type': 'grenade', 'bullet_type': 'projectile', 'cooldown': 180, 'speed': 0, 'damage': 20, 'path': '../assets/weapons/grenade.png', 'length':15, 'auto':False},
			'machine gun': {'ammo_type': 'bullets', 'bullet_type': 'bullet', 'cooldown': 8, 'speed': 0, 'damage': 2, 'path': '../assets/weapons/machine gun.png', 'length':20, 'auto':True},
			'super shotgun': {'ammo_type': 'shells', 'bullet_type': 'bullet', 'cooldown': 80, 'speed': 0, 'damage': 6, 'path': '../assets/weapons/super shotgun.png', 'length':25, 'auto':False},
			'chain gun': {'ammo_type': 'bullets', 'bullet_type': 'bullet', 'cooldown': 10, 'speed': 0, 'damage': 4, 'path': '../assets/weapons/chain gun.png', 'length':22, 'auto':True},
			'grenade launcher': {'ammo_type': 'grenade', 'bullet_type': 'projectile', 'cooldown': 50, 'speed': 0, 'damage': 50, 'path': '../assets/weapons/grenade launcher.png', 'length':15, 'auto':False},
			'rocket launcher': {'ammo_type': 'rockets', 'bullet_type': 'rocket', 'cooldown': 50, 'speed': 2, 'damage': 400, 'path': '../assets/weapons/rocket launcher.png', 'length':20, 'auto':False},
			'railgun': {'ammo_type': 'slugs', 'bullet_type': 'beam', 'cooldown': 30, 'speed': 0, 'damage': 50, 'path': '../assets/weapons/railgun.png', 'length':20, 'auto':False},
			'hyper blaster': {'ammo_type': 'cells', 'bullet_type': 'projectile', 'cooldown': 1, 'speed': 5, 'damage': 50, 'path': '../assets/weapons/hyper_blaster.png', 'length':20, 'auto':True},
			},
	'enemies' :{
			'guard':{'weapon': 'blaster', 'health': 30, 'cooldown': 60, 'burst_count': 3},
			'sg_guard': {'weapon':'shotgun', 'health': 40, 'cooldown': 4, 'burst_count': 3},
			'mg_guard': {'weapon':'machine gun', 'health': 40, 'cooldown': 8, 'burst_count': 3},
			'gladiator': {'weapon':'railgun', 'health': 40, 'cooldown': 8, 'burst_count': 3},
			},

	'abilities':{
			'double_jump': True,
			'dash': False,
			'wall_jump': False,
			'hover': False,
			'ground_smash': False,
			},
		}