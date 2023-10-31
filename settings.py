import pygame

TILESIZE = 16

RES = WIDTH, HEIGHT = pygame.math.Vector2(400,225)#(384, 216)#(512, 288)#(320, 180)#(480, 270)#(640, 360)#(960, 540)#(512, 288)

HALF_WIDTH, HALF_HEIGHT = RES/2

ACTIONS = {'escape':False, 'space':False, 'z':False, 'up':False, 'down':False}

LAYERS = {'blocks':0,
		  'player':1}

FONT = 'fonts/homespun.ttf'

BLACK = (0,0,0)
WHITE = (255, 255, 255)