import pygame, sys, json
from os import walk
from menu import Intro
from settings import *

class Game:
    def __init__(self):

        pygame.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RES))#, pygame.FULLSCREEN|pygame.SCALED)
        self.font = pygame.font.Font(FONT, 10) #int(TILESIZE)) 
        self.running = True
        
        # states
        self.stack = []
        self.load_states()

        # game play timer
        self.last_time = SAVE_DATA['time_elapsed']
        # self.game_timer = Timer(self)

        # slot info
        self.completed_scenes = len(SAVE_DATA['scenes_completed'])
        self.max_num_of_scenes = len(SCENE_DATA.keys())
        self.percent_complete = f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} %"

        self.slot = None
        self.slot_data = self.get_slot_dict()


    def get_slot_dict(self):
        slot_data = {}
        num_of_slots = 5
        for i in range(num_of_slots):
            slot_data.update({str(i+1): {"time_spent": None, "percent_complete": f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} %"}})
        return slot_data

    def write_data(self):
        with open(f"save_file_{self.slot}", "w") as outfile:
            json.dump(SAVE_DATA, outfile)

    def read_data(self):
        if self.slot is not None:
            with open(f"save_file_{self.slot}", 'r') as readfile:
                json_object = json.load(readfile)
                SAVE_DATA.update(json_object)

                self.completed_scenes = len(SAVE_DATA['scenes_completed'])
                self.slot_data[self.slot]['percent_complete'] = f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} % complete"

    def write_data_on_quit(self):
        if self.slot is not None and self.slot in list(self.slot_data.keys()):
            #self.slot_data[self.slot]["time_spent"] = self.timer.add_times(str(PLAYER_DATA['time']), self.timer.get_elapsed_time())
            #PLAYER_DATA.update({'time': self.slot_data[self.slot]["time_spent"]})
            self.write_data()

    #         #print(json_object)

    # def quit_write_data(self):
    #     if self.slot is not None and self.slot in "123":
    #         self.slot_data[self.slot]["time_spent"] = self.timer.add_times(str(PLAYER_DATA['time']), self.timer.get_elapsed_time()) 
    #         PLAYER_DATA.update({'time': self.slot_data[self.slot]["time_spent"]})
    #         self.write_data(PLAYER_DATA, 'player_data')
    #         self.write_data(COMPLETED_DATA,'completed_data')


    def get_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ACTIONS['escape'] = True
                    self.write_data_on_quit()
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
                elif event.key == pygame.K_RETURN:
                    ACTIONS['enter'] = True
               
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
                elif event.key == pygame.K_RETURN:
                    ACTIONS['enter'] = False

            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:
                    ACTIONS['scroll_up'] = True
                elif event.y == -1:
                    ACTIONS['scroll_down'] = True

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

    def render_text(self, text, colour, font, pos, topleft=False):
        surf = font.render(str(text), False, colour)
        rect = surf.get_rect(topleft = pos) if topleft else surf.get_rect(center = pos)
        self.screen.blit(surf, rect)

    def custom_cursor(self, screen):
        surf = pygame.image.load('assets/crosshair.png').convert_alpha()
        rect = surf.get_rect(center = pygame.mouse.get_pos())
        pygame.mouse.set_visible(False)
        surf.set_alpha(150)
        screen.blit(surf, rect)

    def update(self, dt):
        pygame.display.set_caption(str(round(self.clock.get_fps(), 2)))
        self.stack[-1].update(dt)
 
    def draw(self, screen):
        self.stack[-1].draw(screen)
        self.custom_cursor(screen)
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