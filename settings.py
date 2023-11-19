import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,225)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)

HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False, 'left':False, 'right':False, 'enter':False,
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

AMMO_LIMITS = {'normal':{'infinite': 0, 'cells':200, 'shells':100, 'bullets':200, 'grenade':50, 'slugs':50, 'rockets':50},
				'bandolier':{'infinite': 0, 'cells':250, 'shells':150, 'bullets':250, 'grenade':50, 'slugs':75, 'rockets':50},
				'ammo pack':{'infinite': 0, 'cells':300, 'shells':200, 'bullets':300, 'grenade':100, 'slugs':100, 'rockets':100}
				}

AMMO_DATA = {'infinite': 0, 'cells':0, 'shells':0, 'bullets':0,
			'grenade':0, 'slugs':0, 'rockets':0}

SAVE_DATA = {
			'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 100, 'ammo_capacity':'normal',
			'armour_type':'Combat', 'armour':100, 'max_armour':100, 'health':100, 'max_health':100,
			'items':['rebreather','envirosuit','adrenaline','quad damage','invulnerability'],
			'guns_collected':['blaster'],
			}

CONSTANT_DATA = {

	'guns':{
			'blaster': {'ammo_used': 0, 'ammo_type': 'infinite', 'cooldown': 30, 'speed': 4, 'damage': 3, 'length':18, 'auto':False},
			'shotgun': {'ammo_used': 1, 'ammo_type': 'shells', 'cooldown': 80, 'speed': 0, 'damage': 4, 'length':25, 'auto':False},
			'grenade': {'ammo_used': 1, 'ammo_type': 'grenade','cooldown': 180, 'speed': 0, 'damage': 20, 'length':15, 'auto':False},
			'machine gun': {'ammo_used': 1, 'ammo_type': 'bullets', 'cooldown': 8, 'speed': 0, 'damage': 2, 'length':20, 'auto':True},
			'super shotgun': {'ammo_used': 2, 'ammo_type': 'shells','cooldown': 80, 'speed': 0, 'damage': 6, 'length':25, 'auto':False},
			'chain gun': {'ammo_used': 1, 'ammo_type': 'bullets', 'cooldown': 10, 'speed': 0, 'damage': 4, 'length':22, 'auto':True},
			'grenade launcher': {'ammo_used': 1, 'ammo_type': 'grenade', 'cooldown': 50, 'speed': 0, 'damage': 50, 'length':15, 'auto':False},
			'rocket launcher': {'ammo_used': 1, 'ammo_type': 'rockets', 'cooldown': 50, 'speed': 2, 'damage': 400, 'length':20, 'auto':False},
			'railgun': {'ammo_used': 1, 'ammo_type': 'slugs', 'cooldown': 50, 'speed': 0, 'damage': 50, 'length':20, 'auto':False},
			'hyper blaster': {'ammo_used': 1, 'ammo_type': 'cells', 'cooldown': 8, 'speed': 5, 'damage': 5, 'length':23, 'auto':True},
			'BFG10K': {'ammo_used': 50, 'ammo_type': 'cells', 'cooldown': 200, 'speed': 4, 'damage': 100, 'length':20, 'auto':False},
			},
	'enemies' :{
			'guard':{'weapon': 'blaster', 'damage': 5, 'health': 30, 'telegraph_time': 25, 'cooldown': 60, 'burst_count': 3},
			'sg_guard': {'weapon':'machine gun', 'damage': 4, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'mg_guard': {'weapon':'machine gun', 'damage': 5, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'gladiator': {'weapon':'railgun', 'damage': 40, 'health': 40, 'telegraph_time': 25, 'cooldown': 30, 'burst_count': 3},
			},

	'all_items':['rebreather','envirosuit','adrenaline','quad damage','invulnerability'],
		}

