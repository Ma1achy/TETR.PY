from old_state.struct_render import StructRender
from app.utils import lerpBlendRGBA
import pygame

class UIKeyStates():
    def __init__(self, RenderStruct:StructRender, Fonts):
        
        self.RenderStruct = RenderStruct
        self.key_icons = []
        self.key_font = Fonts.key_font
        
        self.left_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.right_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.softdrop_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.harddrop_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.ccw_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.cw_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.colour_180_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        self.hold_surf = pygame.Surface((self.RenderStruct.GRID_SIZE, self.RenderStruct.GRID_SIZE), pygame.SRCALPHA|pygame.HWSURFACE)
        
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
        
        self.key_icons = []
        
        left_colour,         left_alpha     =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_LEFT']               else ((0, 0, 0), 128)
        right_colour,        right_alpha    =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_RIGHT']              else ((0, 0, 0), 128)
        softdrop_colour,     softdrop_alpha =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_SOFT_DROP']          else ((0, 0, 0), 128)
        ccw_colour,          ccw_alpha      =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_COUNTERCLOCKWISE']   else ((0, 0, 0), 128)
        cw_colour,           cw_alpha       =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_CLOCKWISE']          else ((0, 0, 0), 128)
        colour_180,          alpha_180      =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_180']                else ((0, 0, 0), 128)
        harddrop_colour,     harddrop_alpha =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_HARD_DROP']          else ((0, 0, 0), 128)
        hold_colour,         hold_alpha     =     ((255, 255, 255), 256)  if self.RenderStruct.key_dict['KEY_HOLD']               else ((0, 0, 0), 128)

        self.key_icons.append((self.key_font.render('B', True, left_colour),     ((self.RenderStruct.GRID_SIZE // 2, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),   left_alpha,        self.left_surf)))

        self.key_icons.append((self.key_font.render('A', True, right_colour),    ((self.RenderStruct.GRID_SIZE *2 , self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),    right_alpha,       self.right_surf)))

        self.key_icons.append((self.key_font.render('C', True, softdrop_colour), ((self.RenderStruct.GRID_SIZE * 3.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),  softdrop_alpha,    self.softdrop_surf)))

        self.key_icons.append((self.key_font.render('G', True, harddrop_colour), ((self.RenderStruct.GRID_SIZE * 5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),    harddrop_alpha,    self.harddrop_surf)))

        self.key_icons.append((self.key_font.render('E', True, ccw_colour),      ((self.RenderStruct.GRID_SIZE * 6.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),  ccw_alpha,         self.ccw_surf)))

        self.key_icons.append((self.key_font.render('D', True, cw_colour),       ((self.RenderStruct.GRID_SIZE * 8, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),    cw_alpha,          self.cw_surf)))

        self.key_icons.append((self.key_font.render('F', True, colour_180),      ((self.RenderStruct.GRID_SIZE * 9.5, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5),  alpha_180,         self.colour_180_surf)))

        self.key_icons.append((self.key_font.render('H', True, hold_colour),     ((self.RenderStruct.GRID_SIZE * 11, self.RenderStruct.WINDOW_HEIGHT - self.RenderStruct.GRID_SIZE * 1.5) ,  hold_alpha,        self.hold_surf)))

        for surf, (coords, alpha, key_surf) in self.key_icons:
            key_surf.fill((0, 0, 0, 0))
            key_surf.blit(surf, (0, 0))
            key_surf.set_alpha(alpha)
            surface.blit(key_surf, (coords[0], coords[1]))
            
            