import pygame, sys
from os import walk
from intro import Intro
from settings import *

class Game:
    def __init__(self):

        pygame.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RES), pygame.FULLSCREEN|pygame.SCALED)
        self.running = True

        self.font = pygame.font.Font(FONT, int(TILESIZE)) 

        # states
        self.stack = []
        self.load_states()

    def get_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ACTIONS['escape'] = True
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    ACTIONS['space'] = True
                elif event.key == pygame.K_LEFT:
                    ACTIONS['left'] = True
                elif event.key == pygame.K_RIGHT:
                    ACTIONS['right'] = True
                elif event.key == pygame.K_UP:
                    ACTIONS['up'] = True
                elif event.key == pygame.K_DOWN:
                    ACTIONS['down'] = True
                elif event.key == pygame.K_z:
                    ACTIONS['z'] = True
               
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    ACTIONS['space'] = False
                elif event.key == pygame.K_LEFT:
                    ACTIONS['left'] = False
                elif event.key == pygame.K_RIGHT:
                    ACTIONS['right'] = False
                elif event.key == pygame.K_UP:
                    ACTIONS['up'] = False
                elif event.key == pygame.K_DOWN:
                    ACTIONS['down'] = False
                elif event.key == pygame.K_z:
                    ACTIONS['z'] = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    ACTIONS['left_click'] = True
                elif event.button == 3:
                    ACTIONS['right_click'] = True
                elif event.button == 4:
                    ACTIONS['scroll_down'] = True
                elif event.button == 2:
                    ACTIONS['scroll_up'] = True

            if event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1:
                    ACTIONS['left_click'] = False
                elif event.button == 3:
                    ACTIONS['right_click'] = False
                elif event.button == 4:
                    ACTIONS['scroll_down'] = False
                elif event.button == 2:
                    ACTIONS['scroll_up'] = False

    def reset_keys(self):
        for action in ACTIONS:
            ACTIONS[action] = False

    def load_states(self):
        self.intro = Intro(self)
        self.stack.append(self.intro)

    def get_folder_images(self, path):
        surf_list = []
        for _, __, img_files in walk(path):
            for img in img_files:
                full_path = path + '/' + img
                img_surf = pygame.image.load(full_path).convert_alpha()
                surf_list.append(img_surf)

        return surf_list

    def render_text(self, text, colour, font, pos):
        surf = font.render(str(text), False, colour)
        rect = surf.get_rect(topleft = pos)
        self.screen.blit(surf, rect)

    def update(self, dt):
        pygame.display.set_caption(str(round(self.clock.get_fps(), 2)))
        self.stack[-1].update(dt)
 
    def draw(self, screen):
        self.stack[-1].draw(screen)
        pygame.display.flip()

    def main_loop(self):
        dt = self.clock.tick(60)/1000 * 60
        self.get_events()
        self.update(dt)
        self.draw(self.screen)
        
if __name__ == "__main__":
    game = Game()
    while game.running:
        game.main_loop()