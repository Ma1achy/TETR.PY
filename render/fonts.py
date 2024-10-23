from core.state.struct_render import StructRender
import pygame
import os

class Font():
    def __init__(self, size:int = 20):
        """
        Fonts used in the game
        
        args:
            size (int): The size of the font
        """
        self.size = size
        self.base_path = os.path.join(os.path.dirname(__file__), 'font')
    
    def hun2(self):
        font_path = os.path.join(self.base_path, 'hun2.ttf')
        return pygame.font.Font(font_path, self.size)
    
    def pfw(self):
        font_path = os.path.join(self.base_path, 'pfw.ttf')
        return pygame.font.Font(font_path, self.size)
    
    def cr(self):
        font_path = os.path.join(self.base_path, 'cr.ttf')
        return pygame.font.Font(font_path, self.size)
    
    def keystates(self):
        font_path = os.path.join(self.base_path, 'action-icons.ttf')
        return pygame.font.Font(font_path, self.size)

class Fonts():
    def __init__(self, RenderStruct:StructRender):
        """
        Create and store the fonts to be rendered in the game
        """     
        self.RenderStruct = RenderStruct
        pygame.font.init()
    
        self.hun2_biggest = Font(int(self.RenderStruct.GRID_SIZE*3)).hun2()
        self.hun2_bigger = Font(int(self.RenderStruct.GRID_SIZE*1.5)).hun2()
        self.hun2_big = Font(self.RenderStruct.GRID_SIZE).hun2()
        self.hun2_med = Font(3 * self.RenderStruct.GRID_SIZE // 4).hun2()
        self.hun2_small = Font( self.RenderStruct.GRID_SIZE // 2).hun2()
        
        self.slot_big = Font(int(self.RenderStruct.GRID_SIZE*1.2)).hun2()
        self.slot_small = Font(3 * self.RenderStruct.GRID_SIZE // 5).hun2()

        self.pfw_bigger = Font(int(self.RenderStruct.GRID_SIZE*1.5)).pfw()
        self.pfw_big = Font(self.RenderStruct.GRID_SIZE).pfw()
        self.pfw_med = Font(3 * self.RenderStruct.GRID_SIZE // 4).pfw()
        self.pfw_small = Font(self.RenderStruct.GRID_SIZE // 2).pfw()
        
        self.key_font = Font(self.RenderStruct.GRID_SIZE).keystates()
        
        