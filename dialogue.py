import pygame
from state import State
from settings import *

class Dialogue(State):
    def __init__(self, game, text, text_colour, pos=(RES/2)):
        super().__init__(game)

        self.game = game
        self.text = text
        self.pos = pos
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
            if self.timer > 12 * dt:
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
            text_surf = self.game.ui_font.render(str(rendered_line), False, self.text_colour)
            text_rect = text_surf.get_rect(topleft = (self.pos[0], y_position))
            screen.blit(text_surf, text_rect)
            text_surf.set_alpha(self.alpha)
           # self.game.render_text(rendered_line, self.text_colour, self.game.ui_font, (self.center[0], y_position))

    def update(self, dt):
        self.timer += dt
        self.text_update(dt)

    def draw(self, screen):
        self.draw_text(screen)
