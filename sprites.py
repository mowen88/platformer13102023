import pygame, math
from settings import *
from message import Message

class FadeSurf(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, alpha = 255, z = LAYERS['foreground']):
		super().__init__(groups)

		self.game = game
		self.scene = scene
		self.image = pygame.Surface((self.scene.scene_size))
		self.alpha = alpha
		self.loading_text = True
		self.timer = pygame.math.Vector2(self.scene.scene_size).magnitude()/20 # makes load time relative to zone size
		self.fade_duration = 255/20
		self.z = z
		self.rect = self.image.get_rect(topleft = pos)

	def update(self, dt):

		if self.scene.exiting:
			self.alpha += self.fade_duration * dt
			if self.alpha >= 255: 
				self.alpha = 255
				self.scene.exit_state()
				self.scene.create_scene(self.scene.new_scene)
			
		else:
			self.timer -= dt
			if self.timer <= 0:
				self.scene.entering = False
				self.loading_text = False
				self.alpha -= self.fade_duration * dt
				if self.alpha <= 0:
					self.alpha = 0

	def draw(self, screen):
		self.image.set_alpha(self.alpha)
		screen.blit(self.image, (0,0))

		if self.loading_text:
			self.game.render_text('Loading...', NEON_GREEN, self.game.font, (RES/2))

class Collider(pygame.sprite.Sprite):
	def __init__(self, groups, pos, name=None):
		super().__init__(groups)
		self.image = pygame.Surface((TILESIZE, TILESIZE))
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

class Glow(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, surf, z= LAYERS['foreground']):
		super().__init__(groups)
		self.game = game
		self.scene = scene
		self.image = surf
		self.rect = self.image.get_rect(center = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.old_hitbox = self.hitbox.copy()
		self.z = z
		self.alpha = 120

	def update(self, dt):
		self.image.set_alpha(self.alpha)
		self.rect.center = self.scene.player.rect.center

class SecretTile(pygame.sprite.Sprite):
	def __init__(self, game, scene, groups, pos, surf=pygame.Surface((TILESIZE, TILESIZE)), z= LAYERS['foreground']):
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
			self.scene.message = Message(self.game, self.scene, [self.scene.update_sprites], 'You have found a secret.', (HALF_WIDTH, HEIGHT - TILESIZE * 1.5))
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

class Liquid(Tile):
	def __init__(self, groups, pos, surf, z, alpha):
		super().__init__(groups, pos, surf, z)

		self.image.fill(NEON_GREEN)
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.alpha = alpha

	def update(self, dt):
		self.image.set_alpha(self.alpha)


class Pickup(Tile):
	def __init__(self, groups, pos, surf, z, name):
		super().__init__(groups, pos, surf, z)

		self.rect = self.image.get_rect(bottomleft = pos)
		self.hitbox = self.rect.copy().inflate(0,0)
		self.name = name
		
class AnimatedPickup(AnimatedTile):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name):
		super().__init__(game, scene, groups, pos, z, path, animation_type)
		self.name = name

	def update(self, dt):
		self.animate(0.2 * dt)

class MovingPlatform(pygame.sprite.Sprite):
	def __init__(self, groups, pos, surf, z, direction, amplitude, circular=None):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)	
		self.z = z
		self.circular = circular
		self.hitbox = self.rect.copy()
		self.raycast_box = self.hitbox.copy().inflate(0,2)
		self.old_hitbox = self.hitbox.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		
		self.direction = pygame.math.Vector2(direction)
		self.vel = pygame.math.Vector2()
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

class Barrel(pygame.sprite.Sprite):
	def __init__(self, scene,  groups, pos, surf, z):
		super().__init__(groups)

		self.scene = scene
		self.image = surf
		self.rect = self.image.get_rect(bottomleft = pos)	
		self.z = z
		self.hitbox = self.rect.copy()
		self.raycast_box = self.hitbox.copy().inflate(0,2)
		self.old_hitbox = self.hitbox.copy()
		self.pos = pygame.math.Vector2(self.rect.bottomleft)
		self.vel = pygame.math.Vector2()
		self.exploded = False

	def explode(self):
		
		self.scene.create_particle('explosion', self.rect.center)
		for sprite in self.scene.destructible_sprites:
			distance = self.scene.get_distance_direction_and_angle(sprite.rect.center, self.rect.center - self.scene.drawn_sprites.offset)[0]
			if distance < 50:
				sprite.scene.create_particle('explosion', sprite.rect.center)
				sprite.kill()

	def update(self, dt):
		if self.exploded:
			self.explode()

class Door(AnimatedPickup):
	def __init__(self, game, scene, groups, pos, z, path, animation_type, name, new_level=None):
		super().__init__(game, scene, groups, pos, z, path, animation_type, name)

		self.rect = self.image.get_rect(bottomleft=pos)
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.75, -self.rect.height * 0.75)

	def open(self, dt):
		if self.rect.colliderect(self.scene.player.rect):
			
			self.frame_index += 0.2 * dt
			if self.frame_index >= len(self.frames) -1:
				self.frame_index = len(self.frames) -1
			else:
				self.frame_index = self.frame_index % len(self.frames)


		else:
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

		

		

