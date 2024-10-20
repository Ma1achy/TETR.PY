from utils import Font
from core.state.struct_render import StructRender
import pygame


class Fonts():
    def __init__(self, RenderStruct:StructRender):
        
        self.RenderStruct = RenderStruct
        
        pygame.font.init()
        
        self.hun2_big_size = self.RenderStruct.GRID_SIZE
        self.hun2_med_size = 3 * self.RenderStruct.GRID_SIZE // 4
        self.hun2_small_size = self.RenderStruct.GRID_SIZE // 2
        self.pfw_small_size = self.RenderStruct.GRID_SIZE // 2
        self.key_font_size = self.RenderStruct.GRID_SIZE
        
        self.hun2_big = Font(self.hun2_big_size).hun2()
        self.hun2_med = Font(self.hun2_med_size).hun2()
        self.hun2_small = Font(self.hun2_small_size).hun2()
        self.pfw_small = Font(self.pfw_small_size).pfw()
        self.key_font = Font(self.key_font_size).keystates()
        
        