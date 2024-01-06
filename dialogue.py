import pygame
from state import State
from settings import *

class Dialogue(State):
    def __init__(self, game, text, text_colour, pos=(RES/2), can_exit=False):
        super().__init__(game)

        self.game = game
        self.text = text
        self.pos = pos
        self.can_exit = can_exit

        # text box variables
        self.text_colour = text_colour
        self.box_width = 0
        self.target_width = TILESIZE * 10
        self.line_spacing = TILESIZE
        self.lines = self.text
        self.char_indices = [0] * len(self.lines)
        self.done = False
        self.timer = 0
        self.alpha = 255

    def text_update(self, dt):
        if not self.char_indices[-1] >= len(self.lines[-1]):
            if self.timer > 0.5:
                self.timer = 0
                 
                for line in range(len(self.lines)):
                    self.char_indices[line] += 1 
                    if self.char_indices[line] > len(self.lines[line]):
                        self.char_indices[line] = len(self.lines[line])
                    else:
                        break
        else:
            self.done = True

    def draw_text(self, screen):
        total_height = len(self.lines) * self.line_spacing
        start_y = self.pos[1] - total_height // 2
        
        for index, line in enumerate(self.lines):
            rendered_line = self.lines[index][:self.char_indices[index]]
            y_position = start_y + self.line_spacing * index
            text_surf = self.game.font.render(str(rendered_line), False, self.text_colour)
            black_surf = pygame.Surface((text_surf.get_width(), text_surf.get_height() + 2))

            text_surf.set_alpha(self.alpha)
            black_surf.set_alpha(self.alpha)
            
            if self.can_exit:
                text_rect = text_surf.get_rect(midtop = (self.pos[0], y_position))
                screen.blit(black_surf, text_rect)
                screen.blit(text_surf, text_rect)
            else:
                text_rect = text_surf.get_rect(topleft = (self.pos[0], y_position))
                screen.blit(text_surf, text_rect)

           # self.game.render_text(rendered_line, self.text_colour, self.game.ui_font, (self.center[0], y_position))

    def fade_logic(self, dt):

        if self.timer > 50:
            self.alpha -= 5 * dt
            if self.alpha <= 0:
                self.exit_state()
            
    def fade_draw(self, screen):
        if self.can_exit:
            self.prev_state.draw(screen)

    def update(self, dt):
        if self.can_exit:
            self.fade_logic(dt)
        
        if not self.done:
            self.game.item_fx['key_press'].play()

        self.timer += dt

        self.text_update(dt)

    def draw(self, screen):
        if self.can_exit:
            self.fade_draw(screen)
        self.draw_text(screen)
