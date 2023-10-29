import pygame, math, random
from settings import *

class Camera(pygame.sprite.Group):
    def __init__(self, game, scene):
        super().__init__()

        self.game = game
        self.scene = scene
        self.offset = pygame.math.Vector2()

    # def zone_limits(self):
    #     if self.offset[0] <= 0: self.offset[0] = 0
    #     elif self.offset[0] >= self.zone.size[0] - WIDTH: self.offset[0] = self.zone.size[0] - WIDTH
    #     if self.offset[1] <= 0: self.offset[1] = 0
    #     elif self.offset[1] >= self.zone.size[1] - HEIGHT: self.offset[1] = self.zone.size[1] - HEIGHT

    def offset_draw(self, target):
        self.game.screen.fill((255,200,255))

        self.offset += (target - RES//2 - self.offset)

        for layer in LAYERS.values():
            for sprite in self.scene.drawn_sprites:
                if sprite.z == layer:
                    offset = sprite.rect.topleft - self.offset
                    self.game.screen.blit(sprite.image, offset)