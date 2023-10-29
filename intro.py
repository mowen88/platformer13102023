from state import State
from scene import Scene
from settings import *

class Intro(State):
	def __init__(self, game):
		State.__init__(self, game)

	def update(self, dt):
		if ACTIONS['space']:
			Scene(self.game).enter_state()
			ACTIONS['space'] = False

	def draw(self, screen):
		screen.fill((255,255,200))