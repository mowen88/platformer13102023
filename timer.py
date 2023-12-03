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

	def stop(self):
		self.running = False
		self.toggle_count = 0
		self.timer = 0
		self.running = False
		self.var = False
		return self.var

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

class GameTimer:
	def __init__(self, game):
		self.game = game

		self.active = False
		self.secs = 0
		self.mins = 0
		self.hours = 0
		self.elapsed_time = SAVE_DATA['time_elapsed']

	def add_times(self, time1, time2):
		hours1, mins1, secs1 = map(int, time1.split(':'))
		hours2, mins2, secs2 = map(int, time2.split(':'))
		
		total_hours = hours1 + hours2
		total_mins = mins1 + mins2
		total_secs = secs1 + secs2

		total_mins += total_secs//60
		total_secs %= 60
		total_hours += total_mins//60
		total_mins %= 60

		result = "%02d:%02d:%02d" % (total_hours, total_mins, total_secs)

		return result

	def get_elapsed_time(self):
	    return "%02d:%02d:%02d" % (self.hours, self.mins, self.secs)

	def reset(self):
		self.elapsed_time = 0

	def stop_start(self):
		self.active = not self.active

	def update(self, dt):
		if self.active:
			self.elapsed_time += dt/60 

			self.hours = int(self.elapsed_time//3600)
			self.mins = int((self.elapsed_time % 3600)//60)
			self.secs = int(self.elapsed_time % 60)
			