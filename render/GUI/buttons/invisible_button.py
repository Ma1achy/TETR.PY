from render.GUI.buttons.button import Button
import pygame

class InvisibleButton(Button):
    def __init__(self, Timing, surface, Mouse, function, container):
        super().__init__(Timing, surface, Mouse, function, container, width = container.width, height = container.height, offset = (0, 0), style = None, maintain_alpha = False)

        self.get_rect_and_surface()