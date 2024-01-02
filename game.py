import pygame, sys, os, json, cProfile
from pygame import mixer
from os import walk
from menu import PygameLogo
from timer import GameTimer
from settings import *

class Game:
    def __init__(self):
 
        mixer.init()
        pygame.init()

        pygame.mixer.music.load('audio/music/soundtrack.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1, 0.2, 5000)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RES), pygame.FULLSCREEN|pygame.SCALED)
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
        self.slot_data = self.get_slot_dict(6)

        self.weapon_fx = self.import_sfx('audio/sfx/weapons') 
        self.world_fx = self.import_sfx('audio/sfx/world') 
        self.item_fx = self.import_sfx(f'audio/sfx/items')

    def import_sfx(self, path, volume=0.2):
        sfx_dict = {}

        for root, _, sfx_files in os.walk(path):
            for sfx in sfx_files:
                full_path = os.path.join(root, sfx)
                sfx_name, sfx_ext = os.path.splitext(sfx)

                if sfx_ext.lower() == '.wav':
                    sound = pygame.mixer.Sound(full_path)
                    sound.set_volume(volume)
                    sfx_dict[sfx_name] = sound

        return sfx_dict

        # self.landing_fx = pygame.mixer.Sound('audio/sfx/player/landing_grunt.wav') 
        # self.landing_fx.set_volume(0.2)

    def get_slot_dict(self, num_of_slots):
        slot_data = {}
        for i in range(1, num_of_slots+1):
            slot_data.update({str(i): {"time_spent": "00:00:00", "percent_complete": f"{int(self.completed_scenes/self.max_num_of_scenes * 100)} %"}})
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
        self.pygame_logo = PygameLogo(self)
        self.stack.append(self.pygame_logo)

    def get_csv_layer(self, path):
        grid = []
        with open(path) as layout:
            layer = reader(layout, delimiter = ',')
            for row in layer:
                grid.append(list(row))
            return grid

    def get_folder_images(self, path):
        surf_list = []
        for _, __, img_files in walk(path):
            for img in img_files:
                full_path = path + '/' + img
                img_surf = pygame.image.load(full_path).convert_alpha()
                surf_list.append(img_surf)
        return surf_list
 
    def render_text(self, text, colour, font, pos, topleft=False):
        surf = font.render (str(text), False, colour)
        rect = surf.get_rect(topleft = pos) if topleft else surf.get_rect(center = pos)
        self.screen.blit(surf, rect)

    def custom_cursor(self, screen):
        surf = pygame.image.load('assets/crosshair.png').convert_alpha()
        rect = surf.get_rect(center = pygame.mouse.get_pos())
        pygame.mouse.set_visible(False)
        surf.set_alpha(150)
        screen.blit(surf, rect)

    def update(self, dt):
        #pygame.display.set_caption(str(round(self.clock.get_fps(), 2)))
        self.timer.update(dt)
        self.stack[-1].update(dt)
 
    def draw(self, screen):
        self.stack[-1].draw(screen)
        self.custom_cursor(screen)
        pygame.display.flip()

    def main_loop(self):
        dt = self.clock.tick(60) * 0.06
        self.get_events()
        self.update(dt)
        self.draw(self.screen)
        
if __name__ == "__main__":
    game = Game()
    while game.running:
        game.main_loop()
        #cProfile.run("game.main_loop()", sort="cumulative")

