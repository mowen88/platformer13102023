import pygame, sys, json
from os import walk
from menu import Intro
from timer import GameTimer
from settings import *

class Game:
    def __init__(self):

        pygame.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RES))#, pygame.FULLSCREEN|pygame.SCALED)
        self.font = pygame.font.Font(FONT, 9) #int(TILESIZE))
        self.ui_font = pygame.font.Font(FONT, 16) #int(TILESIZE)) 
        self.running = True
        
        # states
        self.stack = []
        self.load_states()

        # game play timer
        self.last_time = SAVE_DATA['time_elapsed']
        self.timer = GameTimer(self)

        # slot info
        self.completed_scenes = len(SAVE_DATA['scenes_completed'])
        self.max_num_of_scenes = len(SCENE_DATA.keys())
        self.percent_complete = f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} %"
        self.last_time = SAVE_DATA['time_elapsed']
        self.timer = GameTimer(self)
        self.slot = None
        self.slot_data = self.get_slot_dict()

    def get_slot_dict(self):
        slot_data = {}
        num_of_slots = 5
        for i in range(1, num_of_slots):
            slot_data.update({str(i): {"time_spent": None, "percent_complete": f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} %"}})
        return slot_data

    def write_data(self):

        with open(f"save_file_{self.slot}", "w") as write_save_file:
            json.dump(COMMIT_SAVE_DATA, write_save_file)
        with open(f"ammo_file_{self.slot}", "w") as write_ammo_file:
            json.dump(COMMIT_AMMO_DATA, write_ammo_file)

    def read_data(self):
        
        with open(f"save_file_{self.slot}", 'r') as read_save_file:
            save_json = json.load(read_save_file)
            SAVE_DATA.update(save_json)

        with open(f"ammo_file_{self.slot}", 'r') as read_ammo_file:
            ammo_json = json.load(read_ammo_file)
            AMMO_DATA.update(ammo_json)

            self.completed_scenes = len(SAVE_DATA['scenes_completed'])
            self.slot_data[self.slot]['percent_complete'] = f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} % complete"

    def read_slot_progress(self, slot, data_type): 
        with open(f"save_file_{slot}", 'r') as read_save_file:
            save_json = json.load(read_save_file)
            if data_type == 'level':
                return SCENE_DATA[save_json['current_scene']]['level']
            elif data_type == 'unit':
                return SCENE_DATA[save_json['current_scene']]['unit']
            else:
                return save_json[data_type]

    def write_game_time(self):
        if self.slot is not None and self.slot in list(self.slot_data.keys()):
            self.slot_data[self.slot]["time_spent"] = self.timer.add_times(str(SAVE_DATA['time_elapsed']), self.timer.get_elapsed_time()) 
            COMMIT_SAVE_DATA.update({'time_elapsed': self.slot_data[self.slot]["time_spent"]})
            with open(f"save_file_{self.slot}", "r") as read_save_file:
                current_saved_data = json.load(read_save_file)

            current_saved_data['time_elapsed'] = COMMIT_SAVE_DATA['time_elapsed']

            with open(f"save_file_{self.slot}", "w") as write_save_file:
                json.dump(current_saved_data, write_save_file)


    def get_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                self.write_game_time()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ACTIONS['escape'] = True
                    self.write_game_time()
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
        self.timer.update(dt)
        self.stack[-1].update(dt)
        print(len(self.stack))
 
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