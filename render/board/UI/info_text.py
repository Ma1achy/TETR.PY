from core.state.struct_render import StructRender
from core.state.struct_flags import StructFlags
from core.state.struct_timing import StructTiming
from render.board.struct_board import StructBoardConsts
from core.state.struct_gameinstance import StructGameInstance
import pygame

class UIInfoText():
    def __init__(self, RenderStruct:StructRender, FlagStruct:StructFlags, GameInstanceStruct:StructGameInstance, TimingStruct:StructTiming, Fonts, BoardConsts:StructBoardConsts):
        
        self.GameInstanceStruct = GameInstanceStruct
        self.RenderStruct = RenderStruct
        self.FlagStruct = FlagStruct
        self.TimingStruct = TimingStruct
        self.BoardConsts = BoardConsts
        self.Fonts = Fonts
        
        self.slot_width = self.RenderStruct.GRID_SIZE * 5
        self.slot_height =  self.RenderStruct.GRID_SIZE * 1.85
        
        self.left_slot_1_pos = (self.BoardConsts.matrix_rect_pos_x - self.RenderStruct.BORDER_WIDTH - self.RenderStruct.GRID_SIZE * 1.25 - self.slot_width, self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.MATRIX_SURFACE_HEIGHT + self.RenderStruct.BORDER_WIDTH - self.slot_height)
        self.left_slot_2_pos = (self.left_slot_1_pos[0], self.left_slot_1_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        self.left_slot_3_pos = (self.left_slot_1_pos[0], self.left_slot_2_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        self.left_slot_4_pos = (self.left_slot_1_pos[0], self.left_slot_3_pos[1] - self.slot_height - self.RenderStruct.GRID_SIZE * 0.5)
        self.right_slot_1_pos = (self.BoardConsts.matrix_rect_pos_x + self.RenderStruct.BORDER_WIDTH * 2 + self.BoardConsts.MATRIX_SURFACE_WIDTH,  self.BoardConsts.matrix_rect_pos_y + self.BoardConsts.queue_rect_height  + self.RenderStruct.BORDER_WIDTH * 2 + self.RenderStruct.GRID_SIZE)
        
        self.objective_width = self.RenderStruct.GRID_SIZE * 10
        self.objective_height = self.RenderStruct.GRID_SIZE * 5
        self.objective_slot_pos = (self.BoardConsts.matrix_rect_pos_x + self.BoardConsts.MATRIX_SURFACE_WIDTH//2 - self.objective_width // 2, self.BoardConsts.matrix_rect_pos_y + 1*self.BoardConsts.MATRIX_SURFACE_HEIGHT//4 - self.objective_height // 2)
        
        # TODO: create surfaces that you can choose to render different counters/timers/info onto
        # they will then be blitted onto the board surface in the correct position
        self.slots = {
            0: 'STOPWATCH',
            1: 'STOPWATCH',
            2: 'STOPWATCH',
            3: 'STOPWATCH',
            4: 'STOPWATCH',
            5: 'STOPWATCH',
        }
         
    def draw(self, surface):
        """
        
        args:
            surface (pygame.Surface): The surface to draw onto
        """
        self.get_slots(surface)
        
        self.__format_time()

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
            objective_slot_rect = pygame.Rect(self.objective_slot_pos[0], self.objective_slot_pos[1],  self.objective_width, self.objective_height)
           # pygame.draw.rect(surface, (255, 255, 255), objective_slot_rect, 1)
            return self.objective_slot_pos, objective_slot_rect
        
    def get_slots(self, surface):
        
        for slot in self.slots:
            match self.slots[slot]:
                case 'STOPWATCH':
                    self.__draw_timer(slot, surface)
                case None:
                    pass
                case _:
                    self.__draw_missing_slot(slot, surface, self.slots[slot]) # handle case when unknown slot type is passed
        
    def __format_time(self):
        """
        Format the time in seconds into the format 'mm:ss' and 'ms'
        
        returns:
            time_minsec (str): the time in the format 'mm:ss'
            time_ms (str): the time in milliseconds
        """
        minutes = int((self.TimingStruct.current_time % 3600) // 60)
        seconds = int(self.TimingStruct.current_time % 60)
        milliseconds = int((self.TimingStruct.current_time % 1) * 1000)
        time_minsec = f"{minutes}:{seconds:02}"
        time_ms = f"{milliseconds:03}"
        return time_minsec, time_ms
    
    def __draw_timer(self, slot, surface): 
        """
        Draw the timer
        
        args:
            surface (pygame.Surface): The surface to draw
        """
        
        if not self.FlagStruct.GAME_OVER:
            self.time_minsec, self.time_ms = self.__format_time()
        
        slot_pos, slot_rect = self.get_slot_rects(surface, slot)
        
        if slot == 4: # left aligned
            
            text_time_minsec = self.Fonts.slot_big.render(f'{self.time_minsec}.', True, (255, 255, 255))
            text_time_minsec_rect = text_time_minsec.get_rect()
            text_time_minsec_position = (slot_rect.bottomleft[0], slot_rect.bottomleft[1] - text_time_minsec_rect.height)
            
            text_time_ms = self.Fonts.hun2_med.render(self.time_ms, True, (255, 255, 255))
            text_time_ms_rect = text_time_ms.get_rect()
            text_time_ms_position = (text_time_minsec_position[0] + text_time_minsec_rect.width + self.RenderStruct.GRID_SIZE * 0.05, text_time_minsec_position[1] + text_time_minsec_rect.height - text_time_ms_rect.height - (self.Fonts.slot_big.get_height() - self.Fonts.hun2_med.get_height()) / 4)
            
            text_time = self.Fonts.slot_small.render('TIME', True, (255, 255, 255))
            text_time_rect = text_time.get_rect()
            text_time_position = (slot_rect.topleft[0], slot_rect.topleft[1])
            
            surface.blit(text_time_ms, text_time_ms_position)
            surface.blit(text_time_minsec, text_time_minsec_position)
            surface.blit(text_time, text_time_position)
        
        elif slot == 5: # objective
            
            objective_surface = pygame.Surface((self.objective_width, self.objective_height), pygame.SRCALPHA)
            
            text_time_minsec = self.Fonts.hun2_biggest.render(f'{self.time_minsec}.', True, (255, 255, 255))
            text_time_minsec_rect = text_time_minsec.get_rect()
            
            text_time_ms = self.Fonts.hun2_med.render(self.time_ms, True, (255, 255, 255))
            text_time_ms_rect = text_time_ms.get_rect()
            
            text_time_minsec_position = (self.objective_width / 2 - text_time_minsec_rect.width / 2 - text_time_ms_rect.width / 2, self.objective_height / 2 - text_time_minsec_rect.height / 2)
            text_time_ms_position = (text_time_minsec_position[0] + text_time_minsec_rect.width + self.RenderStruct.GRID_SIZE * 0.2, text_time_minsec_position[1] + text_time_minsec_rect.height - text_time_ms_rect.height - (self.Fonts.hun2_biggest.get_height() - self.Fonts.hun2_med.get_height())/5)

            # self.Fonts.hun2_biggest.set_bold(True)
            # self.Fonts.hun2_med.set_bold(True)
            
            text_time_minsec_outline  = self.Fonts.hun2_biggest_bold.render(f'{self.time_minsec}.', True, (105, 105, 105))
            text_time_ms_outline = self.Fonts.hun2_med_bold.render(self.time_ms, True, (105, 105, 105))
            
            # self.Fonts.hun2_biggest.set_bold(False)
            # self.Fonts.hun2_med.set_bold(False)
            
            text_time_minsec_outline_position = (text_time_minsec_position[0], text_time_minsec_position[1])
            text_time_ms_outline_position = (text_time_ms_position[0], text_time_ms_position[1])
           
            objective_surface.blit(text_time_minsec_outline, text_time_minsec_outline_position)
            objective_surface.blit(text_time_ms_outline, text_time_ms_outline_position)
            
            objective_surface.blit(text_time_ms, text_time_ms_position)
            objective_surface.blit(text_time_minsec, text_time_minsec_position)
            objective_surface.set_alpha(88)  # (0-255, where 0 is fully transparent and 255 is fully opaque)
            
            surface.blit(objective_surface, slot_rect.topleft)
            
        else: # right aligned 
            
            text_time_ms = self.Fonts.hun2_med.render(self.time_ms, True, (255, 255, 255))
            text_time_ms_rect = text_time_ms.get_rect()
            text_time_ms_position = (slot_rect.bottomright[0] - text_time_ms_rect.width, slot_rect.bottomright[1] - text_time_ms_rect.height)
            
            text_time_minsec = self.Fonts.slot_big.render(f'{self.time_minsec}.', True, (255, 255, 255))
            text_time_minsec_rect = text_time_minsec.get_rect()
            text_time_minsec_position = (text_time_ms_position[0] - text_time_minsec_rect.width - self.RenderStruct.GRID_SIZE * 0.05, text_time_ms_position[1] + text_time_ms_rect.height - text_time_minsec_rect.height + (self.Fonts.slot_big.get_height() - self.Fonts.hun2_med.get_height()) / 4)
            
            text_time = self.Fonts.slot_small.render('TIME', True, (255, 255, 255))
            text_time_rect = text_time.get_rect()
            text_time_position = (slot_rect.bottomright[0] - text_time_rect.width, slot_rect.topright[1])
            
            surface.blit(text_time_ms, text_time_ms_position)
            surface.blit(text_time_minsec, text_time_minsec_position)
            surface.blit(text_time, text_time_position)
        
        # pygame.draw.rect(surface, (255, 255, 255), (text_time_ms_position[0], text_time_ms_position[1], text_time_ms_rect.width, text_time_ms_rect.height), 1)
        # pygame.draw.rect(surface, (255, 255, 255), (text_time_minsec_position[0], text_time_minsec_position[1], text_time_minsec_rect.width, text_time_minsec_rect.height), 1)
        # pygame.draw.rect(surface, (255, 255, 255), (text_time_position[0], text_time_position[1], text_time_rect.width, text_time_rect.height), 1)

    def __draw_missing_slot(self, slot, surface, passed):
        
        slot_pos, slot_rect = self.get_slot_rects(surface, slot)
        pygame.draw.rect(surface, (255, 0, 255), slot_rect)
        
        text = self.Fonts.hun2_small.render(f'???: {passed}', True, (0,  0, 0))
        text_rect = text.get_rect()
        text_pos = (slot_rect.centerx - text_rect.width // 2, slot_rect.centery - text_rect.height // 2)
        surface.blit(text, text_pos)
        
        
        