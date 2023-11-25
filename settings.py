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
BLUE = (20,68,145)
NEON_BLUE = (120, 215, 225)
NEON_GREEN = (61, 255, 110)
DARK_GREEN = (5, 33, 55)
YELLOW = (255, 255, 64)
BROWN = (110, 74, 57)
LIGHT_GREY = (146,143,184)

SCENE_DATA = {
			   '0':{'1':'1', '3':'1'}, 
  			   '1':{'1':'0', '2':'2', '3':'0'},
  			   '2':{'2':'1','3':'0'}
  			}

AMMO_LIMITS = {None:{'infinite': 0, 'cells':200, 'shells':100, 'bullets':200, 'grenades':50, 'slugs':50, 'rockets':50},
				'bandolier':{'infinite': 0, 'cells':250, 'shells':150, 'bullets':250, 'grenades':50, 'slugs':75, 'rockets':50},
				'ammo pack':{'infinite': 0, 'cells':300, 'shells':200, 'bullets':300, 'grenades':100, 'slugs':100, 'rockets':100}
				}

AMMO_DATA = {'infinite': 0, 'cells':0, 'shells':0, 'bullets':0,
			'grenades':5, 'slugs':0, 'rockets':0}
ARMOUR_DATA = {None:[0,0],'jacket':[25,50],'combat':[50, 100],'body':[100, 200]}

SAVE_DATA = {
			'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 0, 'ammo_capacity':None,
			'armour_type':None, 'armour':0, 'max_armour':0, 'health':100, 'max_health':100,
			'items':['rebreather','envirosuit','adrenaline','quad damage','invulnerability'],
			'guns_collected':['blaster', 'hand grenade'],'keys_collected':['red key']
			}

CONSTANT_DATA = {

	'guns':{
			'blaster': {'ammo_given': 0, 'ammo_used': 0, 'ammo_type': 'infinite', 'cooldown': 30, 'speed': 4, 'damage': 3, 'length':18, 'auto':False},
			'shotgun': {'ammo_given': 20, 'ammo_used': 1, 'ammo_type': 'shells', 'cooldown': 80, 'speed': 0, 'damage': 4, 'length':25, 'auto':False},
			'hand grenade': {'ammo_given': 5, 'ammo_used': 1, 'ammo_type': 'grenades','cooldown': 120, 'speed': 0, 'damage': 0, 'length':20, 'auto':False},
			'machine gun': {'ammo_given': 50, 'ammo_used': 1, 'ammo_type': 'bullets', 'cooldown': 8, 'speed': 0, 'damage': 2, 'length':20, 'auto':True},
			'super shotgun': {'ammo_given': 10, 'ammo_used': 2, 'ammo_type': 'shells','cooldown': 80, 'speed': 0, 'damage': 6, 'length':25, 'auto':False},
			'chain gun': {'ammo_given': 200, 'ammo_used': 1, 'ammo_type': 'bullets', 'cooldown': 10, 'speed': 0, 'damage': 4, 'length':22, 'auto':True},
			'grenade launcher': {'ammo_given': 5, 'ammo_used': 1, 'ammo_type': 'grenades', 'cooldown': 50, 'speed': 0, 'damage': 0, 'length':15, 'auto':False},
			'rocket launcher': {'ammo_given': 5, 'ammo_used': 1, 'ammo_type': 'rockets', 'cooldown': 50, 'speed': 2, 'damage': 400, 'length':20, 'auto':False},
			'railgun': {'ammo_given': 10, 'ammo_used': 1, 'ammo_type': 'slugs', 'cooldown': 50, 'speed': 0, 'damage': 50, 'length':20, 'auto':False},
			'hyper blaster': {'ammo_given': 100, 'ammo_used': 1, 'ammo_type': 'cells', 'cooldown': 8, 'speed': 5, 'damage': 5, 'length':23, 'auto':True},
			'BFG10K': {'ammo_given': 50, 'ammo_used': 50, 'ammo_type': 'cells', 'cooldown': 200, 'speed': 4, 'damage': 100, 'length':20, 'auto':False},
			},
	'enemies' :{
			'guard':{'weapon': 'blaster', 'damage': 5, 'health': 30, 'telegraph_time': 25, 'cooldown': 60, 'burst_count': 3},
			'sg_guard': {'weapon':'machine gun', 'damage': 4, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'mg_guard': {'weapon':'machine gun', 'damage': 5, 'health': 40, 'telegraph_time': 25, 'cooldown': 8, 'burst_count': 8},
			'gladiator': {'weapon':'railgun', 'damage': 40, 'health': 40, 'telegraph_time': 25, 'cooldown': 30, 'burst_count': 3},
			},

	'all_items':['rebreather','envirosuit','adrenaline','quad damage','invulnerability'],
		}

