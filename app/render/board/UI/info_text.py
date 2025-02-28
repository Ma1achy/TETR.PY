from old_state.struct_render import StructRender
from instance.state.flags import Flags
from old_state.struct_timing import StructTiming
from render.board.struct_board import StructBoardConsts
from instance.state.game_state import GameState
import pygame
from app.utils import comma_separate

class UIInfoText():
    def __init__(self, RenderStruct:StructRender, FlagStruct:Flags, GameInstanceStruct:GameState, TimingStruct:StructTiming, Fonts, BoardConsts:StructBoardConsts):
        
        self.GameInstanceStruct = GameInstanceStruct
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.TimingStruct = TimingStruct
        self.BoardConsts = BoardConsts
        self.Fonts = Fonts
        
        self.slot_width = self.RenderStruct.GRID_SIZE * 5
        self.slot_height =  self.RenderStruct.GRID_SIZE * 1.85
        
        if self.BoardConsts.draw_garbage_bar:
            self.left_border_offset = 1.25
        else:
            self.left_border_offset = 0.25
        
        self.left_slot_1_pos = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE *  self.left_border_offset - self.slot_width, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH - self.slot_height)
        self.left_slot_2_pos = (self.left_slot_1_pos[0], self.left_slot_1_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        self.left_slot_3_pos = (self.left_slot_1_pos[0], self.left_slot_2_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        self.left_slot_4_pos = (self.left_slot_1_pos[0], self.left_slot_3_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        
        if self.GameInstanceStruct.queue_previews > 0:
            self.right_slot_1_pos = (self.BoardConsts.matrix_rect_pos_x + self.RenderStruct.BORDER_WIDTH * 2 + self.BoardConsts.MATRIX_SURFACE_WIDTH,  self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.queue_rect_height  + self.RenderStruct.BORDER_WIDTH * 2 + self.RenderStruct.GRID_SIZE)
        else:
            self.right_slot_1_pos = (self.BoardConsts.matrix_rect_pos_x + self.RenderStruct.BORDER_WIDTH * 2 + self.BoardConsts.MATRIX_SURFACE_WIDTH,  self.left_slot_1_pos[1])
            
        self.middle_width = self.RenderStruct.GRID_SIZE * 10
        self.middle_height = self.RenderStruct.GRID_SIZE * 5
        self.objective_slot_pos = (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH//2 - self.middle_width // 2, self.BoardConsts.matrix_rect_pos_y + 1*self.BoardConsts.MATRIX_SURFACE_HEIGHT//4 - self.middle_height // 2)
        
        self.overlay_text_surface = pygame.Surface((self.middle_width, self.middle_height), pygame.SRCALPHA|pygame.HWSURFACE)
        
        # TODO: create surfaces that you can choose to render different counters/timers/info onto
        # they will then be blitted onto the board surface in the correct position
        self.slots = {
            0: 'STOPWATCH',
            1: None,
            2: None,
            3: None,
            4: 'SCORE',
            5: None,
        }
         
    def draw(self, surface):
        """
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.overlay_text_surface.fill((0, 0, 0, 0))
        self.get_slots(surface)

    def get_slot_rects(self, surface, slot):
    
        if slot == 0:
            left_slot_1_rect = pygame.Rect(self.left_slot_1_pos[0], self.left_slot_1_pos[1], self.slot_width, self.slot_height)
           # pygame.draw.rect(surface, (255, 255, 255), left_slot_1_rect, 1)
            return self.left_slot_1_pos, left_slot_1_rect
        
        elif slot == 1:
            left_slot_2_rect = pygame.Rect(self.left_slot_2_pos[0], self.left_slot_2_pos[1], self.slot_width, self.slot_height)
           # pygame.draw.rect(surface, (255, 255, 255), left_slot_2_rect, 1)
            return self.left_slot_2_pos, left_slot_2_rect
        
        elif slot == 2:
            left_slot_3_rect = pygame.Rect(self.left_slot_3_pos[0], self.left_slot_3_pos[1], self.slot_width, self.slot_height)
           # pygame.draw.rect(surface, (255, 255, 255), left_slot_3_rect, 1)
            return self.left_slot_3_pos, left_slot_3_rect
            
        elif slot == 3:
            left_slot_4_rect = pygame.Rect(self.left_slot_4_pos[0], self.left_slot_4_pos[1], self.slot_width, self.slot_height)
           # pygame.draw.rect(surface, (255, 255, 255), left_slot_4_rect, 1)
            return self.left_slot_4_pos, left_slot_4_rect

        elif slot == 4:
            right_slot_1_rect = pygame.Rect(self.right_slot_1_pos[0], self.right_slot_1_pos[1], self.slot_width, self.slot_height)
           # pygame.draw.rect(surface, (255, 255, 255), right_slot_1_rect, 1)
            return self.right_slot_1_pos, right_slot_1_rect
        
        elif slot == 5:
            objective_slot_rect = pygame.Rect(self.objective_slot_pos[0], self.objective_slot_pos[1],  self.middle_width, self.middle_height)
           # pygame.draw.rect(surface, (255, 255, 255), objective_slot_rect, 1)
            return self.objective_slot_pos, objective_slot_rect
        
    def get_slots(self, surface):
        
        for slot in self.slots:
            match self.slots[slot]:
                case 'STOPWATCH':
                    time = self.TimingStruct.current_time
                    self.__draw_timer(slot, time, surface)
                case 'SCORE':
                    value_to_display = 4358790
                    self.draw_commasep_number(surface, slot, value_to_display)
                case None:
                    pass
                case _:
                    self.__draw_missing_slot(slot, surface, self.slots[slot]) # handle case when unknown slot type is passed
        
    def __format_time(self, time):
        """
        Format the time in seconds into the format 'mm:ss' and 'ms'
        
        returns:
            time_minsec (str): the time in the format 'mm:ss'
            time_ms (str): the time in milliseconds
        """
        minutes = int((time % 3600) // 60)
        seconds = int(time % 60)
        milliseconds = int((time % 1) * 1000)
        time_minsec = f"{minutes}:{seconds:02}"
        time_ms = f"{milliseconds:03}"
        return time_minsec, time_ms
    
    def __draw_timer(self, slot, time, surface): 
        """
        Draw a timer
        
        args:
            surface (pygame.Surface): The surface to draw
        """
        slot_pos, slot_rect = self.get_slot_rects(surface, slot)
        
        time_minsec, time_ms = self.__format_time(time)
        
        if slot == 4: 
            self.__draw_timer_left_aligned(surface, slot_rect, time_minsec, time_ms, 'TIME', colour = (255, 255, 255))
        elif slot == 5: 
            self.__draw_timer_overlay(time_minsec, time_ms, surface, slot_rect, main_colour = (255, 255, 255), base_colour = (105, 105, 105))
        else: 
            self.__draw_timer_right_aligned(surface, slot_rect, time_minsec, time_ms, 'TIME', colour = (255, 255, 255))

    def draw_commasep_number(self, surface, slot, value_to_display):
        """
        Draw a comma seperated number
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        slot_pos, slot_rect = self.get_slot_rects(surface, slot)
        
        if slot == 4:
            self.__draw_commasep_number_left_aligned(surface, slot_rect, value_to_display, title = 'SCORE', colour = (255, 255, 255))
        elif slot == 5: 
            self.__draw_comaasep_number_overlay(surface, slot_rect, value_to_display, main_colour = (255, 255, 255), base_colour = (105, 105, 105))
        else:
            self.__draw_commasep_number_right_aligned(surface, slot_rect, value_to_display, title = 'SCORE', colour = (255, 255, 255))
                               
    def __draw_missing_slot(self, slot, surface, passed):
        
        slot_pos, slot_rect = self.get_slot_rects(surface, slot)
        pygame.draw.rect(surface, (255, 0, 255), slot_rect)
        
        text = self.Fonts.hun2_small.render(f'???: {passed}', True, (0,  0, 0))
        text_rect = text.get_rect()
        text_pos = (slot_rect.centerx - text_rect.width // 2, slot_rect.centery - text_rect.height // 2)
        surface.blit(text, text_pos)
        
    def __draw_timer_left_aligned(self, surface, slot_rect, time_minsec, time_ms, title_text, colour = (255, 255, 255)):
        
        text_time_minsec = self.Fonts.slot_big.render(f'{time_minsec}.', True, colour)
        text_time_minsec_rect = text_time_minsec.get_rect()
        text_time_minsec_position = (slot_rect.bottomleft[0], slot_rect.bottomleft[1] - text_time_minsec_rect.height)
        
        text_time_ms = self.Fonts.hun2_med.render(time_ms, True, colour)
        text_time_ms_rect = text_time_ms.get_rect()
        text_time_ms_position = (text_time_minsec_position[0] + text_time_minsec_rect.width + self.RenderStruct.GRID_SIZE * 0.05, text_time_minsec_position[1] + text_time_minsec_rect.height - text_time_ms_rect.height - (self.Fonts.slot_big.get_height() - self.Fonts.hun2_med.get_height()) // 4)
        
        text_time = self.Fonts.slot_small.render(title_text, True, colour)
        text_time_rect = text_time.get_rect()
        text_time_position = (slot_rect.topleft[0], slot_rect.topleft[1])
        
        surface.blit(text_time_ms, text_time_ms_position)
        surface.blit(text_time_minsec, text_time_minsec_position)
        surface.blit(text_time, text_time_position)
    
    def __draw_timer_right_aligned(self, surface, slot_rect, time_minsec, time_ms, title_text, colour):
        
        text_time_ms = self.Fonts.hun2_med.render(time_ms, True, colour)
        text_time_ms_rect = text_time_ms.get_rect()
        text_time_ms_position = (slot_rect.bottomright[0] - text_time_ms_rect.width, slot_rect.bottomright[1] - text_time_ms_rect.height)
        
        text_time_minsec = self.Fonts.slot_big.render(f'{time_minsec}.', True, colour)
        text_time_minsec_rect = text_time_minsec.get_rect()
        text_time_minsec_position = (text_time_ms_position[0] - text_time_minsec_rect.width - self.RenderStruct.GRID_SIZE * 0.05, text_time_ms_position[1] + text_time_ms_rect.height - text_time_minsec_rect.height + (self.Fonts.slot_big.get_height() - self.Fonts.hun2_med.get_height()) // 4)
        
        text_time = self.Fonts.slot_small.render(title_text, True, colour)
        text_time_rect = text_time.get_rect()
        text_time_position = (slot_rect.bottomright[0] - text_time_rect.width, slot_rect.topright[1])
        
        surface.blit(text_time_ms, text_time_ms_position)
        surface.blit(text_time_minsec, text_time_minsec_position)
        surface.blit(text_time, text_time_position)
        
    def __draw_timer_overlay(self, time_minsec, time_ms, surface, slot_rect, main_colour = (255, 255, 255), base_colour = (105, 105, 105)):
            
        text_time_minsec = self.Fonts.hun2_biggest.render(f'{time_minsec}.', True,  main_colour)
        text_time_minsec_rect = text_time_minsec.get_rect()
        
        text_time_ms = self.Fonts.hun2_med.render(time_ms, True,  main_colour)
        text_time_ms_rect = text_time_ms.get_rect()
        
        text_time_minsec_position = (self.middle_width // 2 - text_time_minsec_rect.width / 2 - text_time_ms_rect.width // 2, self.middle_height // 2 - text_time_minsec_rect.height // 2)
        text_time_ms_position = (text_time_minsec_position[0] + text_time_minsec_rect.width + self.RenderStruct.GRID_SIZE * 0.2, text_time_minsec_position[1] + text_time_minsec_rect.height - text_time_ms_rect.height - (self.Fonts.hun2_biggest.get_height() - self.Fonts.hun2_med.get_height())//5)
        
        text_time_minsec_outline  = self.Fonts.hun2_biggest.render(f'{time_minsec}.', True, base_colour )
        text_time_ms_outline = self.Fonts.hun2_med.render(time_ms, True, base_colour)
 
        text_time_minsec_outline_position = (text_time_minsec_position[0] + self.RenderStruct.GRID_SIZE*0.2, text_time_minsec_position[1])
        text_time_ms_outline_position = (text_time_ms_position[0] + 3 * 0.1* self.RenderStruct.GRID_SIZE // 4, text_time_ms_position[1])
        
        self.overlay_text_surface.blit(text_time_minsec_outline, text_time_minsec_outline_position)
        self.overlay_text_surface.blit(text_time_ms_outline, text_time_ms_outline_position)
        
        self.overlay_text_surface.blit(text_time_ms, text_time_ms_position)
        self.overlay_text_surface.blit(text_time_minsec, text_time_minsec_position)
        self.overlay_text_surface.set_alpha(88)  #
        
        surface.blit(self.overlay_text_surface, slot_rect.topleft)
        
    def __draw_commasep_number_left_aligned(self, surface, slot_rect, value_to_display, title, colour = (255, 255, 255)):
        
        title_text = self.Fonts.slot_small.render(title, True, colour)
        title_text_rect = title_text.get_rect()
        
        score_text = self.Fonts.slot_big.render(f'{comma_separate(value_to_display)}', True, colour)
        score_text_rect = score_text.get_rect()
    
        title_text_position = (slot_rect.topleft[0], slot_rect.topleft[1])
        score_text_position = (slot_rect.topleft[0], slot_rect.bottomleft[1] - score_text_rect.height)
        
        surface.blit(title_text, title_text_position)
        surface.blit(score_text, score_text_position)
        
    def __draw_commasep_number_right_aligned(self, surface, slot_rect, value_to_display, title, colour = (255, 255, 255)):
        
        title_text = self.Fonts.slot_small.render(title, True, colour)
        title_text_rect = title_text.get_rect()
        
        score_text = self.Fonts.slot_big.render(f'{comma_separate(value_to_display)}', True, colour)
        score_text_rect = score_text.get_rect()
        
        title_text_position = (slot_rect.topright[0] - title_text_rect.width, slot_rect.topright[1])
        score_text_position = (slot_rect.topright[0] - score_text_rect.width, slot_rect.bottomright[1] - score_text_rect.height)
        
        surface.blit(title_text, title_text_position)
        surface.blit(score_text, score_text_position)
        
    def __draw_comaasep_number_overlay(self, surface, slot_rect, value_to_display, main_colour = (255, 255, 255), base_colour = (105, 105, 105)):
            
        score_text, score_text_rect, font = self.Fonts.dynamic_size_font(f'{comma_separate(value_to_display)}', self.overlay_text_surface, main_colour, start_font = self.Fonts.hun2_biggestest)
        
        score_text_position = (self.middle_width // 2 - score_text_rect.width // 2, self.middle_height // 2 - score_text_rect.height // 2)
        
        score_text_outline, score_text_outline_rect, font = self.Fonts.dynamic_size_font(f'{comma_separate(value_to_display)}', self.overlay_text_surface, base_colour, start_font = self.Fonts.hun2_biggestest)

        score_text_outline_position = (score_text_position[0] + self.Fonts.get_size(font) * 0.0621, score_text_position[1])
        
        self.overlay_text_surface.blit(score_text_outline, score_text_outline_position)
        self.overlay_text_surface.blit(score_text, score_text_position)
        self.overlay_text_surface.set_alpha(88)
        
        surface.blit(self.overlay_text_surface, slot_rect.topleft)