import pygame, math, random
from settings import *

class Camera(pygame.sprite.Group):
    def __init__(self, game, scene):
        super().__init__()

        self.game = game
        self.scene = scene
        self.offset = pygame.math.Vector2()
        self.camera_lag = 40


    # def zone_limits(self):
    #     if self.offset[0] <= 0: self.offset[0] = 0
    #     elif self.offset[0] >= self.zone.size[0] - WIDTH: self.offset[0] = self.zone.size[0] - WIDTH
    #     if self.offset[1] <= 0: self.offset[1] = 0
    #     elif self.offset[1] >= self.zone.size[1] - HEIGHT: self.offset[1] = self.zone.size[1] - HEIGHT

    def offset_draw(self, target):
        self.game.screen.fill((0,0,0))

        #self.offset = target - RES//2
        # self.offset.x += (target[0] - WIDTH/2 - self.offset.x)

        self.offset.x += (target[0] - HALF_WIDTH - (HALF_WIDTH - pygame.mouse.get_pos()[0])/3 - self.offset.x)/self.camera_lag
        self.offset.y += (target[1] - HALF_HEIGHT - (HALF_HEIGHT - pygame.mouse.get_pos()[1])/3 - self.offset.y)/self.camera_lag

        for layer in LAYERS.values():
            for sprite in self.scene.drawn_sprites:
                if sprite.z == layer:
                    offset = sprite.rect.topleft - self.offset
                    self.game.screen.blit(sprite.image, offset)