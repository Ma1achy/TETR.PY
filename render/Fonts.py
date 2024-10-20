from utils import Font
from core.state.struct_render import StructRender
import pygame


class Fonts():
    def __init__(self, RenderStruct:StructRender):
        
        self.RenderStruct = RenderStruct
        
        pygame.font.init()
        
        self.hun2_big = Font(self.RenderStruct.GRID_SIZE).hun2()
        self.hun2_med = Font(3 * self.RenderStruct.GRID_SIZE // 4).hun2()
        self.hun2_small = Font(self.RenderStruct.GRID_SIZE//2).hun2()
        self.pfw_small = Font(self.RenderStruct.GRID_SIZE//2).pfw()
        self.key_font = Font(self.RenderStruct.GRID_SIZE).keystates()