from utils import Vec2, get_tetromino_blocks
from instance.matrix import Matrix
from input.handling.handling import Action
from core.state.struct_flags import FLAG

class Tetromino():
    def __init__(self, type:str, state:int, x:int, y:int, FlagStruct:FLAG, GameInstanceStruct):
        """
        Create the active Tetromino in the game of Four.
        
        Handles the movement, rotation, and collision detection of the active Tetromino piece. 
  
        args:
            Type (str): Type of the piece: ['T', 'S', 'Z', 'L', 'J', 'I', 'O'] 
            State (int): Rotation state of the piece: [0, 1, 2, 3]
            x (int): x position of the piece
            y (int): y position of the piece
            FlagStruct (FLAG): Flags of the game instance
            GameInstanceStruct (StructGameInstance): The game instance struct
        """
        self.type = type
        self.state = state
        self.blocks = get_tetromino_blocks(self.type)
        self.position = self.__get_origin(x, y)
        self.pivot = self.__get_pivot()
        
        self.shadow_position = Vec2(self.position.x, self.position.y)
        self.GameInstanceStruct = GameInstanceStruct
        self.Flags = FlagStruct
        
        self.lowest_pivot_position = self.GameInstanceStruct.matrix.HEIGHT - (self.pivot.y + self.position.y)
        self.lock_delay_counter = 0
        self.max_moves_before_lock = 15
        
        # default state is 0, but this is allows for pre-rotation
        if self.state == 1:
            self.blocks = self.__rotate_cw()
        elif self.state == 2:
            self.blocks = self.__rotate_180()
        elif self.state == 3:
            self.blocks = self.__rotate_ccw()

    def __get_origin(self, x:int, y:int):
        """
        Get the origin of the piece
        
        args:
            x (int): x position of the piece
            y (int): y position of the piece
        """
        match self.type:
            case 'S' | 'Z' | 'J' | 'L' | 'T': 
                x -= 1                                       
                y -= 1
            
            case 'I':                 
                x -= 1
                y -= 1
                
            case 'O':
                x -= 0
                y -= 1
        
        return Vec2(x, y)
    
    def __get_pivot(self):
        """
        Get the geometric center of the piece
        """
        return Vec2(len(self.blocks) / 2, len(self.blocks) / 2)
    
    # ========================================================== MOVEMENT ============================================================
            
    def move(self, action:Action):
        """
        Move the piece in the given direction
        
        args:
            action (Action): The action to perform
        """
        match action:
            case Action.MOVE_LEFT:
                vector = Vec2(-1, 0)
            
            case Action.MOVE_RIGHT:
                vector = Vec2(1, 0)
    
            case _:
                vector = Vec2(0, 0)
                raise ValueError(f"\033[31mInvalid movement action provided!: {action} \033[31m\033[0m")
            
        if self.collision(self.blocks, vector + self.position): # validate movement
            self.Flags.PUSH_HORIZONTAL = vector
            return

        self.Flags.PUSH_HORIZONTAL = False
        self.__reset_lock_delay_valid_movement()
        self.reset_spin_flags() # spin is not valid if the piece can move after a rotation
        self.position += vector
       
    def sonic_move(self, action:Action):
        """
        Move the piece in the given direction 
        
        args:
            action (Action): The action to perform
        """
        match action:
            case Action.SONIC_LEFT:
                vector = Vec2(-1, 0)
            
            case Action.SONIC_RIGHT:
                vector = Vec2(1, 0)
    
            case _:
                vector = Vec2(0, 0)
                raise ValueError(f"\033[31mInvalid movement action provided!: {action} \033[31m\033[0m")
        
        while not self.collision(self.blocks, vector + self.position):    
            self.position += vector
            self.__reset_lock_delay_valid_movement()
            self.reset_spin_flags()
            self.Flags.PUSH_HORIZONTAL = False
        
        if self.collision(self.blocks, self.position + vector):
            self.Flags.PUSH_HORIZONTAL = vector
        
    def sonic_move_and_drop(self, action:Action, PrefSD:bool):
        """
        Apply the sonic move and drop action to the piece within the same action
        2 different implementations are used depending on the value of PrefSD:
            1/ If PrefSD is True, the piece will attempt to move downwards until it cannot move downwards anymore, then it will attempt to move sideways
            2/ If PrefSD is False, the piece will attempt to move sideways until it cannot move sideways anymore, then it will attempt to move downwards
        
        args:
            action (Action): The action to perform
            PrefSD (bool): Prefer Soft Drop Over Movement
        """
        match action:
            case Action.SONIC_LEFT_DROP:
                horizontal_vector = Vec2(-1, 0)
            case Action.SONIC_RIGHT_DROP:
                horizontal_vector = Vec2(1, 0)
            case _:
                raise ValueError(f"\033[31mInvalid movement action provided!: {action} \033[31m\033[0m")

        if PrefSD:
            if not self.collision(self.blocks, self.position + Vec2(0, 1)):
                self.position += Vec2(0, 1)
                self.sonic_move_and_drop(action, PrefSD)
                self.Flags.PUSH_VERTICAL = False
            else:
                self.Flags.PUSH_VERTICAL = Vec2(0, 1)
                if not self.collision(self.blocks, self.position + horizontal_vector):
                    self.__reset_lock_delay_valid_movement()
                    self.reset_spin_flags()
                    self.position += horizontal_vector
                    self.sonic_move_and_drop(action, PrefSD)
                    self.Flags.PUSH_HORIZONTAL = False
                else:
                    self.Flags.PUSH_HORIZONTAL = horizontal_vector
                    return
        else:
            if not self.collision(self.blocks, self.position + horizontal_vector): 
                self.__reset_lock_delay_valid_movement()
                self.reset_spin_flags()
                self.position += horizontal_vector
                self.sonic_move_and_drop(action, PrefSD) 
                self.Flags.PUSH_HORIZONTAL = False
            else:
                self.Flags.PUSH_HORIZONTAL = horizontal_vector
                if not self.collision(self.blocks, self.position + Vec2(0, 1)):
                    self.position += Vec2(0, 1)
                    self.sonic_move_and_drop(action, PrefSD) 
                    self.Flags.PUSH_VERTICAL = False
                else:
                    self.Flags.PUSH_VERTICAL = Vec2(0, 1)
                    return
    
    def attempt_to_move_downwards(self):
        """
        Attempt to move the piece downwards
        """
        if self.collision(self.blocks, self.position + Vec2(0, 1)):
            return
        else:
            self.reset_spin_flags() # spin is not valid if the piece can fall
            self.position = self.position + Vec2(0, 1)
                
    def collision(self, desired_piece_blocks:list, desired_position:Vec2):
        """
        Check if the piece at the desired position will collide with the matrix bounds or other blocks
        
        args:
            desired_piece_blocks (list): The blocks of the piece at the desired position
            desired_position (Vec2): The desired position of the piece
            matrix (Matrix): The matrix object that contains the blocks that are already placed
        
        returns
            (bool): True if the piece will collide, False otherwise
        """
        if any (
            val != 0 and (
                desired_position.x + x < 0 or desired_position.x + x >= self.GameInstanceStruct.matrix.WIDTH or 
                desired_position.y + y <= 0 or desired_position.y + y >= self.GameInstanceStruct.matrix.HEIGHT or 
                self.GameInstanceStruct.matrix.matrix[desired_position.y + y][desired_position.x + x] != 0
            )
            for y, row in enumerate(desired_piece_blocks)
            for x, val in enumerate(row)
        ):
            return True         
        else:
            return False
        
    def get_height(self):
        """
        Get the true height of the piece, ignoring empty rows
        """
        return sum(1 for row in self.blocks if any(cell != 0 for cell in row))
    
    def is_in_buffer_zone(self, matrix:Matrix):
        """
        Test if the piece is in the buffer zone of the matrix, this is the top half of the matrix that does not have a grid background
        
        args:
            matrix (Matrix): The matrix object that contains the blocks that are already placed
        """
        if all(
            self.position.y + y <= matrix.HEIGHT//2 - 1
            for y, row in enumerate(self.blocks)
            for x, val in enumerate(row)
            if val != 0
        ):
            return True
        else:
            return False
    
    # ========================================================== ROTATION ============================================================
    
    def rotate(self, action:Action, kick_table:dict):
        """
        Rotate the piece in the given direction
        
        args:
            action (Action): The action to perform
            kick_table (dict): The kick table to use for the piece
        """
        self.reset_spin_flags() # reset spin flags before rotation to avoid false positives
        kick_table = self.__get_piece_kick_table(kick_table)
            
        match action:
            case Action.ROTATE_CLOCKWISE:    
                desired_state = (self.state + 1) % 4
                rotated_piece = self.__rotate_cw()
        
            case Action.ROTATE_COUNTERCLOCKWISE:
                desired_state = (self.state - 1) % 4
                rotated_piece = self.__rotate_ccw()

            case Action.ROTATE_180:
                desired_state = (self.state + 2) % 4
                rotated_piece = self.__rotate_180()
        
        self.__do_kick_tests(rotated_piece, desired_state, kick_table, offset = 0, action = action)
        
    def __rotate_cw(self):
        """
        Rotate the piece clockwise
        """
        return [list(reversed(col)) for col in zip(*self.blocks)]
    
    def __rotate_ccw(self):
        """
        Rotate the piece counter clockwise
        """
        return [list(col) for col in reversed(list(zip(*self.blocks)))]
    
    def __rotate_180(self):
        """
        Rotate the piece 180 degrees
        """
        return [row[::-1] for row in reversed(self.blocks)]
    
    def __get_piece_kick_table(self, kick_table):
        match self.type:
            case 'T':
                kick_table = kick_table['T_KICKS']
            case 'S':
                kick_table = kick_table['S_KICKS']
            case 'Z':
                kick_table = kick_table['Z_KICKS']
            case 'L':
                kick_table = kick_table['L_KICKS']
            case 'J':
                kick_table = kick_table['J_KICKS']    
            case 'I':
                kick_table = kick_table['I_KICKS']  
            case 'O':
                kick_table = kick_table['O_KICKS']
         
        return kick_table
    
    # ------------------------------------------------ KICK TESTS ------------------------------------------------
              
    def __do_kick_tests(self, rotated_piece:list, desired_state:int, kick_table, offset:int, action):
        """
        Find a valid rotation of the piece by recursively applying kick translations to it
        until a valid rotation is found or no more offsets are available (rotation is invalid).
        
        args:
            rotated_piece (list): The rotated piece
            desired_state (int): Desired rotation state of the piece [0, 1, 2, 3]
            kick_table (dict): The kick table containing the kicks to apply to the piece for the given rotation type
            offset (int): The kick translation to try from the kick table
            
        returns:
            (None): if the rotation is invalid
        """
        self.reset_spin_flags()
        kick = self.__get_kick(kick_table, desired_state, offset)
        
        if kick is None: # no more offsets to try => rotation is invalid
            return

        kick = Vec2(kick.x, -kick.y) # have to invert y as top left of the matrix is (0, 0)
         
        if self.collision(rotated_piece, self.position + kick): 
            self.__do_kick_tests(rotated_piece, desired_state, kick_table, offset + 1, action) 
        else:
            if self.type == 'T':
                self.__Is_T_Spin(offset, desired_state, kick, action)
                
            else: # all other pieces use immobility test for spin detection
                if not self.GameInstanceStruct.allowed_spins == 'STUPID': 
                    self.__is_spin(rotated_piece, kick, action)
            
            self.__reset_lock_delay_valid_movement() 
            self.state = desired_state
            self.blocks = rotated_piece
            self.position += kick
            
            if self.GameInstanceStruct.allowed_spins == 'STUPID': # stupid mode is done at the end of the rotation since we detect if its on the floor
                self.__is_spin(self.blocks, Vec2(0, 0), action)
              
    def __get_kick(self, kick_table, desired_state:int, offset:int):
        """
        Get the kick translation to apply to the piece for the given offset_order
     
        args:
            kick_table (dict): The kick table containing the kicks to apply to the piece for the given rotation type
            initial_state (int): Initial rotation state of the piece: [0, 1, 2, 3]
            desired_state (int): Desired rotation state of the piece: [0, 1, 2, 3]
            offset (int): The kick translation to try from the kick table
        
        returns:
            kick (Vec2): The kick translation to apply to the piece
        """
        
        if offset > len(kick_table[f'{self.state}->{desired_state}']) - 1:
            return None
        else:
            return kick_table[f'{self.state}->{desired_state}'][offset]
    
    # ------------------------------------------------ SPIN TESTS ------------------------------------------------
       
    def __is_spin(self, rotated_piece:int, kick:Vec2, action):
        """
        check if the rotation is a spin: this is when the piece rotates into an position where it is then immobile
        
        args:
            rotated_piece (list): The rotated piece
            kick (Vec2): The kick translation to apply
        """
        if self.GameInstanceStruct.allowed_spins == 'T-SPIN': # only allow T-Spins
            return 
        
        if self.GameInstanceStruct.allowed_spins == 'STUPID': # anything is a spin if the piece is on the floor at the end of the rotation
            if self.is_on_floor(): 
                self.Flags.IS_SPIN = self.type
                self.Flags.IS_MINI = False
                
                self.Flags.SPIN_DIRECTION = action
                self.Flags.SPIN_ANIMATION = True
        else:
            if self.collision(rotated_piece, self.position + kick + Vec2(1, 0)) and self.collision(rotated_piece, self.position + kick + Vec2(-1, 0)) and self.collision(rotated_piece, self.position + kick+ Vec2(0, 1)) and self.collision(rotated_piece, self.position + kick + Vec2(0, -1)):
                self.Flags.IS_SPIN = self.type
                
                if self.GameInstanceStruct.allowed_spins == 'ALL-MINI': # allow t spins and t spin minis, everything else is a mini
                    self.Flags.IS_MINI = True
                    
                elif self.GameInstanceStruct.allowed_spins == 'ALL-SPIN': # allow t spins and t spin minis, everything else is a spin
                    self.Flags.IS_MINI = False
                    
                    self.Flags.SPIN_DIRECTION = action 
                    self.Flags.SPIN_ANIMATION = True
                     
    def __Is_T_Spin(self, offset:int, desired_state:int, kick:Vec2, action):
        """
        Test if the T piece rotation is a T-spin.
        
        A Spin is a T spin if:
            1/ 3 out of 4 corners of the T piece are filled and the piece "faces" 2 of the filled corners.
            2/ The direction a T piece faces is the direction the non-flat side of the T piece "points".
        
        A Spin is a T-Spin Mini if:
            1/ 1 corner of the T piece is filled and the piece "faces" the filled corner.
            2/ The 2 back corners of the T piece are filled.
        
            Exceptions to T-Spin Mini:
                If the last kick translation was used when rotating from 0 to 3, it is a full T-spin despite not meeting the above conditions.
                If the last kick translation was used when rotating from 2 to 1, it is a full T-spin despite not meeting the above conditions.  
        
        args:
            offset (int): The kick translation to try from the kick table
            desired_state (int): Desired rotation state of the piece [0, 1, 2, 3]
            kick (Vec2): The kick translation to apply  
        """
        corner_pairs = {
            0: [Vec2(0, 0), Vec2(2, 0)],
            1: [Vec2(2, 0), Vec2(2, 2)],
            2: [Vec2(2, 2), Vec2(0, 2)],
            3: [Vec2(0, 2), Vec2(0, 0)]
        }
            
        filled_corners = self.__test_corners(corner_pairs[desired_state], kick) # do facing test
            
        if len(filled_corners) == 1: # 1 corner test for T-Spin Mini
    
            filled_corners = self.__test_corners(corner_pairs[(desired_state + 2) % 4], kick) # do back corner test
            
            if len(filled_corners) > 1:
                
                if offset == 4: # exception to T-Spin Mini (https://tetris.wiki/T-Spin) if the last kick offset was used it is a full t spin
                    self.Flags.IS_SPIN = self.type
                    self.Flags.IS_MINI = False
                    
                    self.Flags.SPIN_DIRECTION = action
                    self.Flags.SPIN_ANIMATION = True
                else:
                    if not self.GameInstanceStruct.allowed_spins == 'STUPID':
                        self.Flags.IS_SPIN = self.type
                        self.Flags.IS_MINI = True
                    else:
                        self.Flags.IS_SPIN = self.type
                        self.Flags.IS_MINI = False
                        
                        self.Flags.SPIN_DIRECTION = action
                        self.Flags.SPIN_ANIMATION = True
            
        elif len(filled_corners) == 2: # 2 corner test for T-Spin
        
            corners = [Vec2(0, 0), Vec2(2, 0), Vec2(0, 2), Vec2(2, 2)]
            filled_corners = self.__test_corners(corners, kick)
            
            if len(filled_corners) >= 3: # 3 corner test for T-Spin
                self.Flags.IS_SPIN = self.type
                self.Flags.IS_MINI = False
                
                self.Flags.SPIN_DIRECTION = action
                self.Flags.SPIN_ANIMATION = True
        else:
            self.Flags.IS_SPIN = False
            self.Flags.IS_MINI = False
    
    def __test_corners(self, corners:list, kick:Vec2):
        """
        Test if the corners of the pieces bounding box are occupied
        
        args:
            corners (list): The corners of the piece bounding box
            kick (Vec2): The kick translation to apply
        
        returns:
            filled_corners (list): The corners that are occupied
        """
        return [
            corner for _, corner in enumerate(corners)
            if (
                (corner_pos := self.position + kick + corner).x < 0 or 
                corner_pos.x >= self.GameInstanceStruct.matrix.WIDTH or 
                corner_pos.y < 0 or 
                corner_pos.y >= self.GameInstanceStruct.matrix.HEIGHT or 
                self.GameInstanceStruct.matrix.matrix[corner_pos.y][corner_pos.x] != 0
            )
        ]
            
    # ========================================================== LOCK DELAY ============================================================
    
    def is_on_floor(self):
        """
        Check if the piece is on the floor
        """
        return self.collision(self.blocks, self.position + Vec2(0, 1))
    
    def reset_lock_delay_lower_pivot(self):
        """
        Update the lowest pivot position of the piece and reset the lock delay if it is 
        lower than the previous lowest pivot position
        """
        pivot_pos_y = self.GameInstanceStruct.matrix.HEIGHT - (len(self.blocks) / 2 + self.position.y)

        if pivot_pos_y < self.lowest_pivot_position:
            self.lowest_pivot_position = pivot_pos_y
            self.lock_delay_counter = 0
            self.max_moves_before_lock = 15
        
        return self.lowest_pivot_position
    
    def __reset_lock_delay_valid_movement(self):
        """
        Reset the lock delay due to valid movement
        """
        self.lock_delay_counter = 0
        
        if self.is_on_floor():
            self.max_moves_before_lock += -1
    
    # ========================================================== GHOST PIECE ============================================================
     
    def shadow(self):
        """
        Create a shadow of the piece that shows where the piece will land
        """
        self.shadow_position = Vec2(self.position.x, self.position.y)
        
        while not self.collision(self.blocks, self.shadow_position):
            self.shadow_position.y += 1
            
        self.shadow_position.y -= 1
        self.shadow_position.x = self.position.x 
    
    def reset_spin_flags(self):
        self.Flags.IS_SPIN = False
        self.Flags.IS_MINI = False