import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,225)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)

VISIBLE_WINDOW_RECT = 0, 0, WIDTH * 2, HEIGHT * 2

HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False, 'left':False, 'right':False, 'enter':False,
			'left_click':False, 'right_click':False, 'scroll_up':False, 'scroll_down':False}

LAYERS = {'background':0,
		  'objects':1,
		  'player':2,
		  'particles':3,
		  'liquid':4,
		  'blocks':5,
		  'secret_blocks':6,
		  'foreground':7}

FONT = 'fonts/homespun.ttf'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (212, 30, 60)
BLUE = (20,68,145)
NEON_BLUE = (120, 215, 225)
NEON_GREEN = (150, 225, 60)
DARK_GREEN = (23, 35, 23)
YELLOW = (255, 255, 64)
BROWN = (110, 74, 57)
DARK_BROWN = (23, 15, 11)
LIGHT_GREY = (146,143,184)

TUTORIALS = {
		'fire':'Left click to fire, right click to jump',
		'jump':'Right click to jump',
		'double_jump':'Right click in air to double jump',
		'crouch':'Hold down to crouch and right click to drop through platform',
		'inventory':'Press enter to use use inventory and click item to use',
		'door':'Press up at a door to enter',
		}

INTRO_TEXT = {
			  0:['Years have passed since the Strogg attacked', 'earth, harvesting humans, continuing to augment', 'themselves with the biological components', 'of all who stand in their way.'],
			  1: ['Humanity launches operation overlord', 'to counter-attack Stroggos.'],
			  2:["Marine Bitterman's drop pod is knocked of", "course by the Strogg's planetry defences, and",'lands miles away from the target drop zone...']
			  }

DIALOGUE = {0:['This is a line of dialogue', 'and this is another line !']}

SCENE_DATA = { # UNIT 1 - BASE
			   # Outer Base
			   '0':{'unit':'base', 'level':'outer base', '1':'1', '3':'1', '6':'2'}, 
  			   '1':{'unit':'bunker', 'level':'outer base', '1':'0', '2':'2', '3':'0','4':'3'},
  			   '2':{'unit':'base', 'level':'outer base', '2':'3','3':'3','7':'0'},
  			   '3':{'unit':'base', 'level':'outer base', '4':'1','2':'2'},
  			   # Comm Center
  			   


  			   # UNIT 2 - BUNKER
  			   # Ammo Depot
  			   #'3':{'unit':'bunker', 'level':'ammo depot', '1':'4','4':'4','3':'2'},
  			   #'4':{'unit':'bunker', 'level':'ammo depot', '1':'3','2':'3','3':'0'},
  			   # Warehouse
  			   # '5':{'unit':'bunker', 'level':'Warehouse', '2':'1','3':'0'},
  			}

AMMO_LIMITS = {'normal':{'infinite': 0, 'cells':200, 'shells':100, 'bullets':200, 'grenades':50, 'slugs':50, 'rockets':50},
				'bandolier':{'infinite': 0, 'cells':250, 'shells':150, 'bullets':250, 'grenades':50, 'slugs':75, 'rockets':50},
				'ammo pack':{'infinite': 0, 'cells':300, 'shells':200, 'bullets':300, 'grenades':100, 'slugs':100, 'rockets':100}
				}
HEALTH_DATA = {'stimpack': 2, 'first aid': 10, 'medkit': 25}


ARMOUR_DATA = {'normal':[0,0],'shard':[2,250],'jacket':[25,50],'combat':[50, 100],'body':[100, 200]}

AMMO_DATA = {'infinite': 0, 'cells':0, 'shells':0, 'bullets':0,
			'grenades':5, 'slugs':0, 'rockets':0}

COMMIT_AMMO_DATA = {'infinite': 0, 'cells':0, 'shells':0, 'bullets':0,
			'grenades':5, 'slugs':0, 'rockets':0}

SAVE_DATA = {
			'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 0, 'ammo_capacity':'normal',
			'armour_type':'normal', 'armour':0, 'max_armour':0, 'shards': 0, 'stimpacks': 0, 'health':100, 'max_health':100,
			'items':[], 'guns_collected':['blaster', 'hand grenade'],
			'keys_collected':[], 'killed_sprites':[], 'scenes_completed':[], 'time_elapsed': 0
			}

COMMIT_SAVE_DATA = {
			'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 0, 'ammo_capacity':'normal',
			'armour_type':'normal', 'armour':0, 'max_armour':0, 'shards': 0, 'stimpacks': 0, 'health':100, 'max_health':100,
			'items':[], 'guns_collected':['blaster', 'hand grenade'],
			'keys_collected':[], 'killed_sprites':[], 'scenes_completed':[], 'time_elapsed': "00:00:00"
			}

INITIAL_DATA = {
			'current_scene':'0', 'entry_pos':'0', 'gun_index':0, 'ammo': 0, 'ammo_capacity':'normal',
			'armour_type':'normal', 'armour':0, 'max_armour':0, 'shards': 0, 'stimpacks': 0, 'health':100, 'max_health':100,
			'items':['rebreather','envirosuit', 'quad damage', 'invulnerability'], 'guns_collected':['blaster', 'hand grenade'],
			'keys_collected':['red key'], 'killed_sprites':[], 'scenes_completed':[], 'time_elapsed': 0
			}

CONSTANT_DATA = {
	'liquid_damage':{
			'lava': 20, 'slime': 5, 'water': 0
			},
	'guns':{
			'blaster': {'ammo_given': 0, 'ammo_used': 0, 'ammo_type': 'infinite', 'cooldown': 30, 'speed': 4, 'damage': 3, 'length':20, 'auto':False},
			'shotgun': {'ammo_given': 20, 'ammo_used': 1, 'ammo_type': 'shells', 'cooldown': 10, 'speed': 0, 'damage': 4, 'length':25, 'auto':False},
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
			'enforcer': {'weapon':'chain gun', 'damage': 3, 'health': 40, 'telegraph_time': 30, 'cooldown': 8, 'burst_count': 12},
			'gladiator': {'weapon':'railgun', 'damage': 40, 'health': 40, 'telegraph_time': 25, 'cooldown': 30, 'burst_count': 3},
			},

	'all_items':['rebreather','envirosuit','adrenaline','quad damage','invulnerability', 'blue key'],
		}

