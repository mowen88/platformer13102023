import pygame
from settings import *

class Timer:
	def __init__(self, duration, toggle_duration, max_toggles):

		self.duration = duration
		self.toggle_duration = toggle_duration
		self.timer = 0
		self.running = False
		self.var = True
		self.toggle_count = 0
		self.max_toggles = max_toggles
		self.countdown = (duration + (max_toggles * toggle_duration))//60

	def start(self):
		self.countdown = (self.duration + (self.max_toggles * self.toggle_duration))//60
		self.running = True

	def update(self, dt):
		if self.running:
			self.timer += dt
			self.countdown = max(0, self.countdown - dt/60)
			if self.timer < self.duration:
				self.var = True
			elif self.timer > self.duration + self.toggle_duration:
				self.var = not self.var
				self.timer = self.duration
				self.toggle_count += 1
				if self.toggle_count > self.max_toggles:
					self.running = False
					self.toggle_count = 0
					self.timer = 0

			return self.var
			