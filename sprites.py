import pygame, math
from settings import *
from message import Message
#from intermission import Intermission
from demo_end import Intermission

class FadeSurf(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, alpha = 255, z = LAYERS['foreground']):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.image = pygame.Surface((WIDTH *2, HEIGHT*2))
		self.alpha = alpha
		self.fade_duration = 15
		self.z = z
		self.rect = self.image.get_rect(center = pos)
		self.get_load_time_and_text()

	def get_load_time_and_text(self):
		if SCENE_DATA[self.scene.current_scene]['level'] != self.scene.prev_level:
			self.timer = pygame.math.Vector2(self.scene.scene_size).magnitude()/5 # makes load time relative to zone size
			self.loading_text = True
		else:
			self.timer = pygame.math.Vector2(self.scene.scene_size).magnitude()/15 # makes load time relative to zone size
			self.loading_text = False

	def update(self, dt):

		# exit logic
		if self.scene.exiting:
			self.alpha += self.fade_duration * dt
			if self.alpha >= 255: 
				self.alpha = 255
				self.scene.exit_state()
				if SCENE_DATA[self.scene.current_scene]['unit'] != SCENE_DATA[self.scene.new_scene]['unit']:
					#Intermission(self.game, self.scene, self.scene.new_scene).enter_state()
					Intermission(self.game).enter_state()
				else:
					self.scene.create_scene(self.scene.prev_level, self.scene.new_scene)
		
		# entering logic
		else: 
			self.timer -= dt
			if self.timer <= 0:
				self.loading_text = False
				self.alpha -= self.fade_duration * dt
				if self.alpha <= 0:
					self.alpha = 0

	def draw(self, screen):
		self.image.set_alpha(self.alpha)
		screen.blit(self.image, self.rect)

		if self.loading_text:
			self.game.render_text('loading...', WHITE, self.game.font, (RES/2))

class HurtSurf(FadeSurf):
	def __init__(self, game, scene, groups, pos, alpha=255, z = LAYERS['foreground']):
		super().__init__(game, scene, groups, pos, alpha)
		self.image = pygame.image.load('assets/hurt_surf.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (WIDTH + 10, HEIGHT + 10))
		self.rect = self.image.get_rect(center = pos)

	def update(self, dt):
		if self.scene.player.hurt:
			self.alpha -= self.fade_duration * dt
			if self.alpha <= 0:
				self.alpha = 0
				self.scene.player.hurt = False
		else:
			self.alpha = 255

	def draw(self, screen):
		self.image.set_alpha(self.alpha)
		screen.blit(self.image, self.rect)


class Collider(pygame.sprite.Sprite):
	def __init__(self, groups, pos, size, name=None):
		super().__init__(groups)
		self.image = pygame.Surface((size))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(2,0)
		self.name = name

class Tile(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE)), z= LAYERS['blocks']):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z

class Tutorial(pygame.sprite.Sprite):
	def __init__(self, groups, rect, text=''):
		super().__init__(groups)

		self.rect = pygame.Rect(rect)
		self.text = text

class SecretTile(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE)), z= LAYERS['secret_blocks']):
		super().__init__(groups)
		self.game = game
		self.scene = scene
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z
		self.alpha = 255
		self.activated = False

	def update_alpha(self, rate, dt):
		if self.activated:
			
			# play sound once when alpha is 255
			if self.alpha == 255:
				self.scene.world_fx['secret'].play()

			self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'You have found a secret', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
			self.alpha -= rate * dt

			if self.alpha < 0:
				for sprite in self.scene.secret_sprites:
					sprite.kill()

			self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.update_alpha(10, dt) 

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, z, path, animation_type=None):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.z = z
		self.animation_type = animation_type
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

		self.hitbox = self.rect.copy().inflate(0,0)
		self.alive = True

	def animate(self, animation_speed):

		self.frame_index += animation_speed

		if self.animation_type == 'loop':
			self.frame_index = self.frame_index % len(self.frames)

		elif self.animation_type == 'end':
			if self.frame_index > len(self.frames)-1:
				self.frame_index = len(self.frames)-1
		else:
			if self.frame_index > len(self.frames)-1:
				self.kill()

		self.image = self.frames[int(self.frame_index)]

	def update(self, dt):
		self.animate(0.2 * dt)

class Liquid(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf, z, name, alpha=140):
		super().__init__(groups)

		self.z = z
		self.name = name
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.alpha = alpha

	def update(self, dt):
		self.image.set_alpha(self.alpha)
		
class AnimatedPickup(AnimatedTile):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name, floating = True):
		super().__init__(game, scene, groups, pos, z, path, animation_type)
		self.name = name
		self.rect = self.image.get_rect(midbottom = pos) if not floating else self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)

	def update(self, dt):
		self.animate(0.2 * dt)

# class Platform(pygame.sprite.Sprite):
# 	def __init__(self, scene, groups, pos, surf, z):
# 		super().__init__(groups)

# 		self.scene = scene
# 		self.image = surf
# 		self.rect = self.image.get_rect(bottomleft = pos)	
# 		self.z = z
# 		self.hitbox = self.rect.copy()
# 		self.old_hitbox = self.hitbox.copy()
# 		self.raycast_box = pygame.Rect(self.hitbox.x, self.hitbox.y -4, self.hitbox.width, 4)

# 	def on_off(self):
# 		if not self.scene.player.drop_through and self.scene.player.old_hitbox.bottom <= self.hitbox.top and self.scene.player.hitbox.bottom > self.hitbox.top:
# 			if self.scene.player.hitbox.colliderect(self.raycast_box):
# 				self.scene.block_sprites.add(self)
# 		else:
# 			self.scene.block_sprites.remove(self)

# 	def update(self, dt):
# 		self.on_off()


class Platform(pygame.sprite.Sprite):
	def __init__(self, scene, groups, pos, surf, z):
		super().__init__(groups)

		self.scene = scene
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)	
		self.z = z
		self.hitbox = self.rect.copy()
		self.raycast_box = pygame.Rect(self.hitbox.x, self.hitbox.y -4, self.hitbox.width, 4)#self.hitbox.copy().inflate(0,2)
		self.old_hitbox = self.hitbox.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.vel = pygame.math.Vector2(0,0)

class Barrel(Platform):
	def __init__(self, scene, groups, pos, surf, z):
		super().__init__(scene, groups, pos, surf, z)

		self.exploded = False

	def explode(self):
		
		self.scene.screenshaking = True
		self.scene.create_particle('explosion', self.rect.center)

		for sprite in self.scene.destructible_sprites:
			distance = self.scene.get_distance_direction_and_angle(sprite.rect.center, self.rect.center - self.scene.drawn_sprites.offset)[0]
			if distance < 50:
				sprite.scene.create_particle('explosion', sprite.rect.center)
				sprite.kill()

	def update(self, dt):
		#self.on_off()
		if self.exploded:
			self.explode()

class MovingPlatform(Platform):
	def __init__(self, scene, groups, pos, surf, z, direction, amplitude, circular=None):
		super().__init__(scene, groups, pos, surf, z)

		self.scene = scene
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)	
		self.z = z
		
		self.hitbox = self.rect.copy()
		self.raycast_box = pygame.Rect(self.hitbox.x, self.hitbox.y -4, self.hitbox.width, 4)#self.hitbox.copy().inflate(0,2)
		self.old_hitbox = self.hitbox.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		
		self.vel = pygame.math.Vector2()
		self.direction = pygame.math.Vector2(direction)
		self.circular = circular
		self.start_pos = pygame.math.Vector2(self.rect.center)
		self.amplitude = amplitude

	def move(self, dt):
		# Update the position using a sine wave pattern
		self.vel += self.direction * dt

		self.pos.x = self.start_pos.x + self.amplitude * math.sin(self.vel.x)

		if self.circular:
			self.pos.y = self.start_pos.y + self.amplitude * math.cos(self.vel.y)
		else:
			self.pos.y = self.start_pos.y + self.amplitude * math.sin(self.vel.y)

		self.hitbox.centerx = round(self.pos.x)
		self.hitbox.centery = round(self.pos.y)
		self.rect.center = self.hitbox.center
		self.raycast_box.midbottom = self.hitbox.midtop

	def update(self, dt):
		#get pos before it is updated to get the displacement of movement per frame and pass it to the player platform_speed
		self.old_pos = self.pos.copy()
		self.old_hitbox = self.hitbox.copy()
		self.move(dt)

class Door(AnimatedPickup):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name, key_required=None):
		super().__init__(game, scene, groups, pos, z, path, animation_type, name)

		self.key_required = key_required
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.75, -self.rect.height * 0.75)
		self.play_sound = True

	def play_sfx(self):
		if len(self.frames) > 1 and self.play_sound:
			if self.key_required in SAVE_DATA['items']:
				self.scene.world_fx['key_use'].play()
			elif self.key_required is not None:
				self.scene.world_fx['key_try'].play()
			else:
				self.scene.world_fx['door'].play()

			self.play_sound = False

	def open(self, dt):

		if self.rect.colliderect(self.scene.player.rect):

			self.play_sfx()
			if self.key_required is None or self.key_required in SAVE_DATA['items']:

				self.frame_index += 0.2 * dt
				if self.frame_index >= len(self.frames) -1:
					self.frame_index = len(self.frames) -1
				else:
					self.frame_index = self.frame_index % len(self.frames)
			else:
				self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], f'You need the {self.key_required}', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))

		else:
			self.play_sound = True

			self.frame_index -= 0.2 * dt
			if self.frame_index <= 0: 
				self.frame_index = 0
			else: 
				self.frame_index = self.frame_index % len(self.frames)

		self.image = self.frames[int(self.frame_index)]

		if self.frame_index == len(self.frames) -1:
			self.scene.exit_sprites.add(self)
		else:
			self.scene.exit_sprites.remove(self)
			
	def update(self, dt):
		
		self.open(dt)
		# else:
		# 	self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], f'You need the {self.name} key', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))

class Trigger(Door):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name):
		super().__init__(game, scene, groups, pos, z, path, animation_type, name)
		self.activated = False

	def activate(self, dt):
		if self.rect.colliderect(self.scene.player.rect) and ACTIONS['up']:
			self.activated = True
		
		if self.activated:
			self.frame_index += 0.2 * dt
			if self.frame_index >= len(self.frames) -1:
				self.frame_index = len(self.frames) -1
		self.image = self.frames[int(self.frame_index)]

		if self.frame_index == len(self.frames) -1:
			for barrier in self.scene.barrier_sprites:
				if barrier.name == self.name:
					barrier.activated = True

	def update(self, dt):
		self.activate(dt)

class Barrier(Door):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name):
		super().__init__(game, scene, groups, pos, z, path, animation_type, name)
		self.activated = False
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()

	def open(self, dt):
		if self.activated:
			self.frame_index += 0.2 * dt
			if self.frame_index >= len(self.frames) -1:
				self.frame_index = len(self.frames) -1
		self.image = self.frames[int(self.frame_index)]

		if self.frame_index == len(self.frames) -1:
			self.scene.block_sprites.remove(self)
		else:
			self.scene.block_sprites.add(self)

	def update(self, dt):
		self.old_hitbox = self.hitbox.copy()
		self.open(dt)

class Laser(Door):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name):
		super().__init__(game, scene, groups, pos, z, path, animation_type, name)
		self.activated = False
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()

	def open(self, dt):
		if self.activated:
			self.frame_index += 0.2 * dt
			if self.frame_index >= len(self.frames) -1:
				self.frame_index = len(self.frames) -1
		self.image = self.frames[int(self.frame_index)]

		if self.frame_index < len(self.frames) -1 and self.rect.colliderect(self.scene.player.hitbox):
			self.scene.player.reduce_health(200)

	def update(self, dt):
		self.old_hitbox = self.hitbox.copy()
		self.open(dt)


class Lever(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, surf, z):
		super().__init__(groups)
		self.game = game
		self.scene = scene
		self.z = z
		self.image_type = pygame.image.load(surf).convert_alpha()
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(bottomleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

		self.rotate = 0
		self.on = False
		self.can_collide = True
		self.max_rotation = 24

	def rotate_sprite(self, dt):
		if self.on:
			self.rotate = min(self.rotate + 2 * dt, self.max_rotation)
		else:
			self.rotate = max(self.rotate - 2 * dt, 0)
		
		self.image = pygame.transform.rotate(self.image_type, self.rotate)
		self.rect = self.image.get_rect(center = self.rect.center)
		self.hitbox.center = self.rect.center

	def update(self, dt):
		if self.scene.player.hitbox.colliderect(self.hitbox) and ACTIONS['up']:
			if self.can_collide:
				self.on = True
				self.can_collide = False
		else:
			self.can_collide = True

		if self.rotate >= self.max_rotation:
			self.rotate = 0
			self.on = False

		self.rotate_sprite(dt)
		self.rect.center = self.hitbox.center

		

		

