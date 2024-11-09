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
        self.base_path = 'resources/font'
    
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

        self.hun2_biggestestest = Font(int(self.RenderStruct.GRID_SIZE*5)).hun2()
        self.hun2_biggestest = Font(int(self.RenderStruct.GRID_SIZE*4)).hun2()
        self.hun2_biggest = Font(int(self.RenderStruct.GRID_SIZE*3)).hun2()
        self.hun2_biggerer = Font(int(self.RenderStruct.GRID_SIZE* 2.25)).hun2()
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
        
    def get_size(self, font):
        """
        Get the size of the font
        
        args:
            font (pygame.font.Font): The font to get the size of
        """
        if font == self.hun2_biggestestest:
            return self.RenderStruct.GRID_SIZE*5
        elif font == self.hun2_biggestest:
            return self.RenderStruct.GRID_SIZE*4
        elif font == self.hun2_biggest:
            return self.RenderStruct.GRID_SIZE*3
        elif font == self.hun2_biggerer:
            return self.RenderStruct.GRID_SIZE*2.25
        elif font == self.hun2_bigger:
            return self.RenderStruct.GRID_SIZE*1.5
        elif font == self.hun2_big:
            return self.RenderStruct.GRID_SIZE
        elif font == self.hun2_med:
            return 3 * self.RenderStruct.GRID_SIZE // 4
        elif font == self.hun2_small:
            return self.RenderStruct.GRID_SIZE // 2
        elif font == self.pfw_bigger:
            return self.RenderStruct.GRID_SIZE*1.5
        elif font == self.pfw_big:
            return self.RenderStruct.GRID_SIZE
        elif font == self.pfw_med:
            return 3 * self.RenderStruct.GRID_SIZE // 4
        elif font == self.pfw_small:
            return self.RenderStruct.GRID_SIZE // 2
        elif font == self.key_font:
            return self.RenderStruct.GRID_SIZE

    def dynamic_size_font(self, text, surf, colour, start_font = None):
            fonts = [
                self.hun2_biggestestest,
                self.hun2_biggestest,
                self.hun2_biggest,
                self.hun2_biggerer,
                self.hun2_bigger,
                self.hun2_big,
                self.hun2_med,
                self.hun2_small
            ]
            
            if start_font and start_font in fonts:
                start_index = fonts.index(start_font)
                fonts = fonts[start_index:]
            
            for font in fonts:
                text_width, text_height = font.size(text)
                
                if text_width <= surf.get_width():
                    rendered_text = font.render(text, True, colour)
                    text_rect = rendered_text.get_rect()
                    return rendered_text, text_rect, font
            
            # If none of the fonts fit, use the smallest font
            font = self.hun2_small
            rendered_text = font.render(text, True, colour)
            text_rect = rendered_text.get_rect()
        
            return rendered_text, text_rect, font