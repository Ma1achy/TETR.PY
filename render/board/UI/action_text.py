from config import StructConfig
from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_timing import StructTiming
from core.state.struct_debug import StructDebug
from render.board.struct_board import StructBoardConsts
import pygame

class UIActionText():
    def __init__(self, GameInstanceStruct:StructGameInstance, RenderStruct:StructRender, FlagStruct:StructFlags, TimingStruct:StructTiming, Fonts, BoardConsts):
 
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.GameInstanceStruct = GameInstanceStruct
        self.TimingStruct = TimingStruct
        self.Fonts = Fonts
        self.BoardConsts = BoardConsts
        
        self.middle_text_surf_width = self.RenderStruct.GRID_SIZE * 10
        self.middle_text_surf_height = self.RenderStruct.GRID_SIZE * 6
        
        if self.BoardConsts.draw_garbage_bar:
            self.left_border_offset = 1.25
        else:
            self.left_border_offset = 0.25
            
        self.overlay_text_surface = pygame.Surface((self.middle_text_surf_width, self.middle_text_surf_height), pygame.SRCALPHA)
            
    def draw(self, surface):
        self.overlay_text_surface.fill((0, 0, 0, 0))
        self.draw_spin_action_text(surface)
        self.draw_line_clear_action_text(surface)
        self.draw_back_to_back_action_text(surface)
        self.draw_combo_action_text(surface)
        self.draw_all_clear_action_text(surface)
    
    def draw_spin_action_text(self, surface):
        if self.FlagStruct.TSPIN:
            text = 'T-SPIN'
            mini_text = None
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['T']
        elif self.FlagStruct.TSPIN_MINI:
            text = 'T-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['T']
        elif self.FlagStruct.IS_SPIN == 'Z':
            text = 'Z-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['Z']
        elif self.FlagStruct.IS_SPIN == 'L':
            text = 'L-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['L']
        elif self.FlagStruct.IS_SPIN == 'O':
            text = 'O-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['O']
        elif self.FlagStruct.IS_SPIN == 'S':
            text = 'S-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['S']
        elif self.FlagStruct.IS_SPIN == 'I':
            text = 'I-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['I']
        elif self.FlagStruct.IS_SPIN == 'J':
            text = 'J-SPIN'
            mini_text = 'MINI '
            colour = self.RenderStruct.COLOUR_MAP_AVG_TEXTURE_COLOUR['J']
        else:
            text = 'SPIN TYPE'
            mini_text = 'MINI '
            colour = (255, 255, 255)
            
        spin_text = self.Fonts.hun2_big.render(text, True, colour)
        spin_text_rect = spin_text.get_rect()
        spin_text_position = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - spin_text_rect.width - self.RenderStruct.GRID_SIZE * self.left_border_offset, self.BoardConsts.matrix_rect_pos_y + spin_text_rect.height + self.RenderStruct.GRID_SIZE * 3.5 + self.RenderStruct.BORDER_WIDTH)
        
        surface.blit(spin_text, spin_text_position)
        
        mini_text_surface = self.Fonts.hun2_med.render(mini_text, True, colour)
        mini_text_rect = mini_text_surface.get_rect()
        mini_text_position = (spin_text_position[0] - mini_text_rect.width, spin_text_position[1] + spin_text_rect.height // 2 - mini_text_rect.height // 2)
        
        surface.blit(mini_text_surface, mini_text_position)
        
        # pygame.draw.rect(surface, colour, (mini_text_position[0], mini_text_position[1], mini_text_rect.width, mini_text_rect.height), 1)
        # pygame.draw.rect(surface, colour, (spin_text_position[0], spin_text_position[1], spin_text_rect.width, spin_text_rect.height), 1)
        
    def draw_line_clear_action_text(self, surface):
        if self.FlagStruct.LINE_CLEAR:
            text = self.get_lines_text()
        else:
            text = 'LINE CLEAR'
                
            text_surface = self.Fonts.hun2_bigger.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            position = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - text_rect.width - self.RenderStruct.GRID_SIZE * self.left_border_offset, self.BoardConsts.matrix_rect_pos_y + text_rect.height + self.RenderStruct.GRID_SIZE * 4 + self.RenderStruct.BORDER_WIDTH)
            
            surface.blit(text_surface, position)
            
            # pygame.draw.rect(surface, (255, 255, 255), (position[0], position[1], text_rect.width, text_rect.height), 1)
        
    def draw_back_to_back_action_text(self, surface):
        multiplier_text = 'MULTI'
        cross_text = 'X'
        b2b_text = 'B2B' + ' '
         
        multiplier_text = self.Fonts.hun2_med.render(multiplier_text, True, (253, 220, 92))
        multiplier_text_rect = multiplier_text.get_rect()
        multiplier_positon = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - multiplier_text_rect.width - self.RenderStruct.GRID_SIZE * self.left_border_offset, self.BoardConsts.matrix_rect_pos_y + multiplier_text_rect.height + self.RenderStruct.GRID_SIZE * 6.25 + self.RenderStruct.BORDER_WIDTH)
        
        cross_text_surface = self.Fonts.hun2_small.render(cross_text, True, (253, 220, 92))
        cross_text_rect = cross_text_surface.get_rect()
        cross_positon = (multiplier_positon[0] - cross_text_rect.width *1.1, multiplier_positon[1] + multiplier_text_rect.height//2 - cross_text_rect.height//2)
        
        b2b_text_surface = self.Fonts.hun2_med.render(b2b_text, True, (253, 220, 92))
        b2b_text_rect = b2b_text_surface.get_rect()
        b2b_positon = (cross_positon[0] - b2b_text_rect.width, multiplier_positon[1])
        
        surface.blit(multiplier_text, multiplier_positon)
        surface.blit(cross_text_surface, cross_positon)
        surface.blit(b2b_text_surface, b2b_positon)
        
        # pygame.draw.rect(surface, (253, 220, 92), (multiplier_positon[0], multiplier_positon[1], multiplier_text_rect.width, multiplier_text_rect.height), 1)
        # pygame.draw.rect(surface, (253, 220, 92), (cross_positon[0], cross_positon[1], cross_text_rect.width, cross_text_rect.height), 1)
        # pygame.draw.rect(surface, (253, 220, 92), (b2b_positon[0], b2b_positon[1], b2b_text_rect.width, b2b_text_rect.height), 1)
        
    def get_lines_text(self):
        if self.FlagStruct.LINE_CLEAR == 1:
            return 'SINGLE'
        elif self.FlagStruct.LINE_CLEAR == 2:
            return 'DOUBLE'
        elif self.FlagStruct.LINE_CLEAR == 3:
            return 'TRIPLE'
        elif self.FlagStruct.LINE_CLEAR == 4:
            return 'QUAD'
        elif self.FlagStruct.LINE_CLEAR == 5:
            return 'PENTUPLE'
        elif self.FlagStruct.LINE_CLEAR == 6:
            return 'SEXTUPLE'
        elif self.FlagStruct.LINE_CLEAR == 7:
            return 'SEPTUPLE'
        elif self.FlagStruct.LINE_CLEAR == 8:
            return 'OCTUPLE'
        elif self.FlagStruct.LINE_CLEAR == 9:
            return 'NONUPLE'
        elif self.FlagStruct.LINE_CLEAR == 10:
            return 'DECUPLE'
        else:
            return 'LINE CLEAR'

    def draw_combo_action_text(self, surface):
        
        combo_text = 'COMBO'
        multiplier_text = 'MULTI' + ' '
        
        combo_text = self.Fonts.hun2_big.render(combo_text, True, (255, 255, 255))
        combo_text_rect = combo_text.get_rect()
        combo_positon = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - combo_text_rect.width - self.RenderStruct.GRID_SIZE * self.left_border_offset, self.BoardConsts.matrix_rect_pos_y + combo_text_rect.height + self.RenderStruct.GRID_SIZE * 7 + self.RenderStruct.BORDER_WIDTH)
        
        multiplier_text_surface = self.Fonts.hun2_bigger.render(multiplier_text, True, (255, 255, 255))
        multiplier_text_rect = multiplier_text_surface.get_rect()
        multiplier_positon = (combo_positon[0] - multiplier_text_rect.width, combo_positon[1] + combo_text_rect.height // 2 - multiplier_text_rect.height // 2)
        
        surface.blit(combo_text, combo_positon)
        surface.blit(multiplier_text_surface, multiplier_positon)
        
        # pygame.draw.rect(surface, (255, 255, 255), (combo_positon[0], combo_positon[1], combo_text_rect.width, combo_text_rect.height), 1)
        # pygame.draw.rect(surface, (255, 255, 255), (multiplier_positon[0], multiplier_positon[1], multiplier_text_rect.width, multiplier_text_rect.height), 1)
    
    def draw_all_clear_action_text(self, surface):
        
        main_colour = (253, 220, 92)
        base_colour = (209, 129, 48)
        
        line_1_text = 'ALL'
        line_2_text = 'CLEAR'
        
        text_surface_rect = self.overlay_text_surface.get_rect()
        
        line1_text, line1_text_rect, font = self.Fonts.dynamic_size_font(line_1_text, self.overlay_text_surface, main_colour, start_font = self.Fonts.hun2_biggest)
   
        line1_text_position = (text_surface_rect.topleft[0] + text_surface_rect.width // 2 - line1_text_rect.width // 2, text_surface_rect.topleft[1])
    
        line1_text_outline, line1_text_rect, font = self.Fonts.dynamic_size_font(line_1_text, self.overlay_text_surface, base_colour, start_font = self.Fonts.hun2_biggest)
        
        line1_text_outline_position = (line1_text_position[0] + self.Fonts.get_size(font) * 0.0621, line1_text_position[1])
        
        line2_text, line2_text_rect, font = self.Fonts.dynamic_size_font(line_2_text, self.overlay_text_surface, main_colour, start_font = self.Fonts.hun2_biggest)

        line2_text_position = (text_surface_rect.topleft[0] + text_surface_rect.width // 2 - line2_text_rect.width // 2, text_surface_rect.bottomleft[1] - line2_text_rect.height)
        
        line2_text_outline, line2_text_rect, font = self.Fonts.dynamic_size_font(line_2_text, self.overlay_text_surface, base_colour, start_font = self.Fonts.hun2_biggest)
        
        line2_text_outline_position = (line2_text_position[0] + self.Fonts.get_size(font) * 0.0621, line2_text_position[1])
        
        self.overlay_text_surface.blit(line1_text_outline, line1_text_outline_position)
        self.overlay_text_surface.blit(line1_text, line1_text_position)
        
        self.overlay_text_surface.blit(line2_text_outline, line2_text_outline_position)
        self.overlay_text_surface.blit(line2_text, line2_text_position)
         
        self.overlay_text_surface.set_alpha(256)  # (0-255, where 0 is fully transparent and 255 is fully opaque)
        surface.blit(self.overlay_text_surface, (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH // 2 - self.middle_text_surf_width // 2, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT / 2 - self.middle_text_surf_height // 2))