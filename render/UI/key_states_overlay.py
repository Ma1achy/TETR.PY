from core.state.struct_render import StructRender
from utils import lerpBlendRGBA

class UIKeyStates():
    def __init__(self, RenderStruct:StructRender, Fonts):
        
        self.RenderStruct = RenderStruct
        self.key_surfaces = []
        self.key_font = Fonts.key_font
        
    def draw(self, surface):
        """
        Draw the key states onto a surface
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.__draw_key_states(surface)
    
    def __draw_key_states(self, surface):
        """
        Draw the current key states
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        if self.RenderStruct.key_dict is None:
            return
        
        self.key_surfaces = []
        
        left_colour = (255, 255, 255)       if self.RenderStruct.key_dict['KEY_LEFT']               else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        right_colour = (255, 255, 255)      if self.RenderStruct.key_dict['KEY_RIGHT']              else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.3)
        softdrop_colour = (255, 255, 255)   if self.RenderStruct.key_dict['KEY_SOFT_DROP']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        ccw_colour = (255, 255, 255)        if self.RenderStruct.key_dict['KEY_COUNTERCLOCKWISE']   else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        cw_colour = (255, 255, 255)         if self.RenderStruct.key_dict['KEY_CLOCKWISE']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        colour_180 = (255, 255, 255)        if self.RenderStruct.key_dict['KEY_180']                else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        harddrop_colour = (255, 255, 255)   if self.RenderStruct.key_dict['KEY_HARD_DROP']          else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        hold_colour = (255, 255, 255)       if self.RenderStruct.key_dict['KEY_HOLD']               else lerpBlendRGBA((0, 0, 0), (255, 255, 255), 0.33)
        
        self.key_surfaces.append((self.key_font.render('B', True, left_colour), (self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('A', True, right_colour), (self.RenderStruct.GRID_SIZE *2 , self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('C', True, softdrop_colour), (self.RenderStruct.GRID_SIZE * 3.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('G', True, harddrop_colour), (self.RenderStruct.GRID_SIZE * 5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('E', True, ccw_colour), (self.RenderStruct.GRID_SIZE * 6.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('D', True, cw_colour), (self.RenderStruct.GRID_SIZE * 8, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('F', True, colour_180), (self.RenderStruct.GRID_SIZE * 9.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        self.key_surfaces.append((self.key_font.render('H', True, hold_colour), (self.RenderStruct.GRID_SIZE * 11, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5)))

        for surf, coords in self.key_surfaces:
            surface.blit(surf, coords)