import pygame
from state import State
from settings import *

class Dialogue(State):
    def __init__(self, game, scene, text, duration):
        super().__init__(game)

        self.game = game
        self.scene = scene
        self.text = text
        self.duration = duration
        self.offset = self.scene.drawn_sprites.offset

        # text box variables
        self.text_colour = WHITE
        self.box_width = 0
        self.target_width = TILESIZE * 10
        self.line_spacing = TILESIZE
        self.lines = self.text
        self.char_indices = [0] * len(self.lines)

        self.timer = 0
        self.alpha = 255
        self.colour = WHITE

        self.cursor_flashing = True


    def text_update(self, dt):
        if not self.char_indices[-1] >= len(self.lines[-1]):
            if self.timer > 2 * dt:
                self.timer = 0

                for line in range(len(self.lines)):
                    self.char_indices[line] += 1 
                    if self.char_indices[line] > len(self.lines[line]):
                        self.char_indices[line] = len(self.lines[line])
                    else:
                        break

    def draw_text(self, screen):
        total_height = len(self.lines) * self.line_spacing
        start_y = HALF_WIDTH - total_height // 2
        
        for index, line in enumerate(self.lines):
            rendered_line = self.lines[index][:self.char_indices[index]]
            y_position = start_y + self.line_spacing * index
            text_surf = self.game.ui_font.render(str(rendered_line), False, self.colour)
            text_rect = text_surf.get_rect(center = (HALF_WIDTH, y_position))
            screen.blit(text_surf, text_rect)
            text_surf.set_alpha(self.alpha)
           # self.game.render_text(rendered_line, self.text_colour, self.game.ui_font, (self.center[0], y_position))

    def update(self, dt):
        self.timer += dt

        self.duration -= dt
        if self.duration < 0:
            self.alpha -= 10 * dt

        self.text_update(dt)

    def draw(self, screen):
        self.draw_text(screen)
