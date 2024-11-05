from instance.tetromino import Tetromino
from instance.matrix import Matrix
from core.handling import Action
from instance.rotation import RotationSystem
import math
from utils import Vec2

class Four():
    def __init__(self, core_instance, matrix_width, matrix_height, rotation_system:str = 'SRS', randomiser = '7BAG', queue_previews = 5, seed = 0, hold = True, allowed_spins = 'ALL-MINI', top_out_ok = False, reset_on_top_out = False):
        """
        Create an instance of the game Four
        
        args:
         (Core): The core instance of the game
            rotation_system (str): The rotation system to use
            
        methods:
            loop(): The main game loop
            forward_state(): Forward the state of the game to allow for async rendering
        """
        self.core_instance = core_instance
        self.Config = core_instance.Config
        self.FlagStruct = core_instance.FlagStruct
        self.GameInstanceStruct = core_instance.GameInstanceStruct
        self.TimingStruct = core_instance.TimingStruct
        self.HandlingStruct = core_instance.HandlingStruct

        self.GameInstanceStruct.rotation_system_type = rotation_system
        self.GameInstanceStruct.rotation_system = RotationSystem(rotation_system)
        self.GameInstanceStruct.kick_table = self.GameInstanceStruct.rotation_system.kick_table
        self.GameInstanceStruct.allowed_spins = allowed_spins
        self.GameInstanceStruct.top_out_ok = top_out_ok
        self.GameInstanceStruct.reset_on_top_out = reset_on_top_out
        
        self.GameInstanceStruct.reset = False
        
        self.GameInstanceStruct.randomiser = randomiser
        self.GameInstanceStruct.seed = seed
        
        if queue_previews > 6:
            queue_previews = 6
            
        self.GameInstanceStruct.queue_previews = queue_previews
        
        self.RNG = RNG(self.GameInstanceStruct.seed)
        self.GameInstanceStruct.queue = Queue(self.RNG, randomiser)
        self.GameInstanceStruct.matrix = Matrix(matrix_width, matrix_height)
        
        self.GameInstanceStruct.hold = hold
    
    # =================================================== GAME LOGIC ===================================================
        
    def loop(self):
        """
        The main game loop
        """
        self.actions_this_tick = []
        self.core_instance.handling.before_loop_hook()
        
        self.__action_dequeuer()
        self.__get_next_state()
           
    def __action_dequeuer(self):
        """
        Consume the actions from the action queue to be performed in the current tick
        """
        if self.core_instance.TPS != 0:
            tick_duration = 1000 / self.core_instance.TPS # ms per tick
        else:
            tick_duration = 1000/ self.Config.TPS
            
        for action_dict in list(self.core_instance.handling.action_queue):
           
            relative_tick = int((action_dict['timestamp'] - self.TimingStruct.current_time) / tick_duration)

            if relative_tick <= 0 and abs(relative_tick) <= self.HandlingStruct.buffer_threshold: # only perform past actions that haven't been performed that are within the buffer threshold or actions that are on this tick
                self.actions_this_tick.append(action_dict)
                self.core_instance.handling.consume_action()
                                
    # --------------------------------------------------- UPDATE ORDER ---------------------------------------------------
       
    def __get_next_state(self):
        """
        Get the next state of the game
        """
        if not self.FlagStruct.GAME_OVER:
        
            self.__perform_actions()
            self.__perform_gravity()
            self.__do_lock_delay()
            self.__clear_lines()
            
            if self.GameInstanceStruct.current_tetromino is None:
                self.__get_next_piece(hold = False)
            
            self.__do_top_out_warning()

            self.__update_current_tetromino()
        
        else:
            if self.GameInstanceStruct.reset_on_top_out:
                self.__do_top_out_warning()
                
                if self.GameInstanceStruct.reset:
                    self.__topout_ok_reset_game()
    
    def __update_current_tetromino(self):
        """
        Update the current tetromino at the end of the tick
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.shadow()
        self.GameInstanceStruct.current_tetromino.reset_lock_delay_lower_pivot()
                
    # ---------------------------------------------------- ACTIONS ---------------------------------------------------
    
    def __perform_actions(self):
        """
        Perform the actions to be done in the current tick
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.__prevent_accidental_hard_drop()
        
        for action_dict in self.actions_this_tick:
            action = action_dict['action'] 
                  
            match action:
                case Action.MOVE_LEFT | Action.MOVE_RIGHT:
                    self.__move(action)
                
                case Action.SONIC_LEFT | Action.SONIC_RIGHT:
                    self.__sonic_move(action)
                    
                case Action.ROTATE_CLOCKWISE | Action.ROTATE_COUNTERCLOCKWISE:
                    self.__rotate90(action)
                        
                case Action.ROTATE_180:
                    self.__rotate180(action)
                        
                case Action.HARD_DROP:
                    if not self.FlagStruct.DO_PREVENT_ACCIDENTAL_HARD_DROP:
                        self.__hard_drop()
                    
                case Action.HOLD:
                    if self.GameInstanceStruct.hold:
                        self.__hold()
                
                case Action.SONIC_DROP:
                    self.__sonic_drop()
                
                case Action.SONIC_LEFT_DROP | Action.SONIC_RIGHT_DROP:
                    self.__sonic_move_and_drop(action)
    
    def __move(self, action):
        """
        Move the current tetromino left or right
        
        args:
            action (Action): The action to perform
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.move(action)
        
    def __rotate90(self, action):
        """
        Rotate the current tetromino by 90 degrees
        
        args:
            action (Action): The action to perform
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.rotate(action, self.GameInstanceStruct.kick_table['90'])
        
    def __rotate180(self, action):
        """
        Rotate the current tetromino by 180 degrees
        
        args:
            action (Action): The action to perform
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.rotate(action, self.GameInstanceStruct.kick_table['180'])
  
    def __hard_drop(self):
        """
        Hard drop the current tetromino
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.FlagStruct.HARD_DROP_BOUNCE = True
        self.__move_to_floor()
        self.__lock()
        
    def __soft_drop(self):
        """
        Soft drop the current tetromino
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.soft_dropping = True
        self.GameInstanceStruct.soft_drop_factor = self.Config.HANDLING_SETTINGS['SDF']
        self.__update_current_tetromino()
    
    def __sonic_move(self, action):
        """
        Move the current tetromino left or right instantly
        
        args:
            action (Action): The action to perform
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.sonic_move(action)
        
    def __sonic_drop(self):
        """
        Perform a sonic drop, moving the current tetromino to the floor instantly
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.__move_to_floor()
        self.FlagStruct.HARD_DROP_BOUNCE  = True
        
    def __sonic_move_and_drop(self, action):
        """
        Move the current tetromino left or right instantly and then instantly move it to the floor
            - if PrefSD is true, the sonic drop will be performed first then the sonic move
            - if PrefSD is false, the sonic move will be performed first then the sonic drop
        args:
            action (Action): The action to perform
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.sonic_move_and_drop(action, self.Config.HANDLING_SETTINGS['PrefSD'])
    
    def __hold(self):
        """
        Hold the current tetromino
        """
        if self.GameInstanceStruct.can_hold:
            self.__get_next_piece(hold = True)
    
    def __lock(self):
        """
        Lock the current tetromino
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.matrix.insert_blocks(self.GameInstanceStruct.current_tetromino.blocks, self.GameInstanceStruct.current_tetromino.position, self.GameInstanceStruct.matrix.matrix)
        self.GameInstanceStruct.current_tetromino = None
            
    def __move_to_floor(self):
        """
        Move the current tetromino to the floor
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        while not self.GameInstanceStruct.current_tetromino.is_on_floor():
            self.GameInstanceStruct.current_tetromino.attempt_to_move_downwards()
    
    def __clear_lines(self):
        """
        Clear full lines from the matrix
        """
        lines_cleared, cleared_blocks, cleared_idxs = self.GameInstanceStruct.matrix.clear_lines()
        
        if lines_cleared is not None:
            self.core_instance.RenderStruct.lines_cleared, self.core_instance.RenderStruct.cleared_blocks, self.core_instance.RenderStruct.cleared_idxs = lines_cleared, cleared_blocks, cleared_idxs
    # --------------------------------------------------- GRAVITY ---------------------------------------------------
    
    def __perform_gravity(self):
        """
        Perform gravity on the current tetromino
        """  
        if self.GameInstanceStruct.current_tetromino is None:
            return
                     
        for action_dict in self.actions_this_tick:
            action = action_dict['action']
            
            if action == Action.SOFT_DROP:
                self.__soft_drop()
                if self.GameInstanceStruct.current_tetromino.is_on_floor():
                    self.FlagStruct.PUSH_VERTICAL = Vec2(0, 1)
                else:
                    self.FlagStruct.PUSH_VERTICAL = False
            else:
                self.FlagStruct.PUSH_VERTICAL = False
                    
        self.__apply_gravity(self.GameInstanceStruct.gravity, self.GameInstanceStruct.soft_drop_factor)     
        
    def __apply_gravity(self, G, soft_drop_factor = 1):
        """
        Apply gravity to the current tetromino
        
        args:
            G (int): The gravity value in blocks per fractions of 1/60th of a second, i.e 1G = 1 block per 1/60th of a second
            soft_drop_factor (int): The factor to scale the gravity by when soft dropping
        """
        if self.GameInstanceStruct.current_tetromino is None or self.GameInstanceStruct.current_tetromino.is_on_floor():
            self.GameInstanceStruct.gravity_counter = 0
            return
        
        if self.GameInstanceStruct.soft_dropping:
            self.__reset_gravity_after_soft_drop()
            
        if soft_drop_factor == 'inf' or G == 20: # instant gravity
            self.__move_to_floor()
            return
        
        elif G == 0 and soft_drop_factor == 1: # do not pefrom gravity
            self.GameInstanceStruct.G_units_in_ticks = 'inf'
            return
        else:
            if G == 0 and soft_drop_factor != 1: # if G = 0 and soft dropping do gravity at level 1 speed
                G = 1/60
                
            # convert G from units of blocks per 1/60 seconds to units of blocks per no. of ticks 
            self.GameInstanceStruct.G_units_in_ticks = int(self.Config.TPS/((G * soft_drop_factor) * 60))
            
            if self.GameInstanceStruct.gravity_counter >= self.GameInstanceStruct.G_units_in_ticks:
                self.__do_gravity()
            else:
                self.GameInstanceStruct.gravity_counter += 1
            
    def __do_gravity(self):
        """
        Do gravity on the current tetromino
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        self.GameInstanceStruct.current_tetromino.attempt_to_move_downwards()
        self.GameInstanceStruct.gravity_counter = 0
    
    def __reset_gravity_after_soft_drop(self):
        """
        Reset the gravity counter after a soft drop so there is no extra time left on the gravity counter,
        and reset the soft drop factor back
        """
        actions = [ac['action'] for ac in self.actions_this_tick]
        
        if Action.SOFT_DROP not in actions:
            self.GameInstanceStruct.soft_dropping = False
            self.GameInstanceStruct.soft_drop_factor = 1 # reset the soft drop factor to handle softdrop release
            self.GameInstanceStruct.gravity_counter = 0
    
    # --------------------------------------------------- PIECE SPAWNING ---------------------------------------------------   
                   
    def __get_next_piece(self, hold:bool):
        """
        Get the next piece from the queue and spawn it
        
        args:
            hold (bool): Whether to hold the current piece
        """
        self.GameInstanceStruct.can_hold = True
        hold_spawn = False
        
        if hold is False:
            next_piece = self.GameInstanceStruct.queue.view_queue(idx = 0)
        else:
            if self.GameInstanceStruct.current_tetromino is None: # to prevent holding during tick when current tetromino is None
                return
        
            if self.GameInstanceStruct.held_tetromino is None:
                next_piece = self.GameInstanceStruct.queue.view_queue(idx = 0)
                self.GameInstanceStruct.held_tetromino = self.GameInstanceStruct.current_tetromino.type
                self.GameInstanceStruct.can_hold = False
                hold_spawn = 'hold'
            else:
                next_piece = self.GameInstanceStruct.held_tetromino
                self.GameInstanceStruct.held_tetromino = self.GameInstanceStruct.current_tetromino.type
                self.GameInstanceStruct.can_hold = False
                hold_spawn = 'swap'
            
        self.__spawn_piece(next_piece, hold_spawn)
            
    def __spawn_piece(self, next_piece:str, hold_spawn:bool):
        """
        Spawn a new tetromino
        
        args:
            next_piece (str): The type of the next tetromino
            hold_spawn (bool): Whether the piece is spawning from the hold slot
        """
        
        self.spawn_pos = Vec2(math.floor((self.GameInstanceStruct.matrix.WIDTH - 1) / 2), self.GameInstanceStruct.matrix.HEIGHT // 2 - 2)
        
        spawning_tetromino = Tetromino(next_piece, 0,  self.spawn_pos.x,  self.spawn_pos.y, self.FlagStruct, self.GameInstanceStruct)
        self.GameInstanceStruct.lock_delay_counter = 0
        
        if hold_spawn == 'swap': # if the piece is being swapped in, insert the blocks before checking if it can spawn (visual consistency otherwise will look like you die for no reason)
            self.GameInstanceStruct.current_tetromino = None
            self.GameInstanceStruct.current_tetromino = spawning_tetromino
            self.__check_spawn(spawning_tetromino)
            self.reset_flags()
        
        elif hold_spawn == 'hold': # if the current piece is being held, normal behaviour
            self.GameInstanceStruct.current_tetromino = None
            if self.__check_spawn(spawning_tetromino):
                self.GameInstanceStruct.queue.get_next_piece()
                self.GameInstanceStruct.current_tetromino = spawning_tetromino
                self.reset_flags()
        else:
            self.GameInstanceStruct.current_tetromino = None
            if self.__check_spawn(spawning_tetromino):
                self.GameInstanceStruct.queue.get_next_piece()
                self.GameInstanceStruct.current_tetromino = spawning_tetromino
                self.reset_flags()
    
    def __check_spawn(self, spawning_tetromino):
        """
        Check if the tetromino can spawn in the matrix
        """
        if not spawning_tetromino.collision(spawning_tetromino.blocks, spawning_tetromino.position):
            return True
        else:
            self.FlagStruct.GAME_OVER = True
            print("Game Over")
            return False
                                
    # --------------------------------------------------- LOCK DELAY ---------------------------------------------------
    
    def __do_lock_delay(self):
        """
        Increment the lock delay counter when the current tetromino is on the floor and lock it when the counter reaches the lock delay
        
        - Lock delay is reset every time a piece is moved or rotated (successfully) (the maximum amount of resets is 15 and every reset subtracts 1 from the total resets)
        - If 15 resets are reached, the piece locks instantly on contact with the floor
        - The move resets are replenished if the piece falls below its lowest position (given by the y coord of the center of rotation of the piece)
        - Each ARR move counts as a reset (this is a bit weird when using 0 ARR but makes sense)
        """
        
        if self.GameInstanceStruct.current_tetromino is None:
            return
        
        if self.GameInstanceStruct.lock_delay == 'inf':
            self.GameInstanceStruct.lock_delay_in_ticks = 'inf'
            return
        else: 
            self.GameInstanceStruct.lock_delay_in_ticks = int(self.GameInstanceStruct.lock_delay/60 * self.Config.TPS) # convert from frames in 1/60th of a second to ticks in 1/self.config.TPS of a second
        
            if self.GameInstanceStruct.current_tetromino.is_on_floor():
                self.GameInstanceStruct.current_tetromino.lock_delay_counter += 1
            else:
                self.GameInstanceStruct.current_tetromino.lock_delay_counter = 0
                
            if self.GameInstanceStruct.current_tetromino.lock_delay_counter >= self.GameInstanceStruct.lock_delay_in_ticks:
                self.__lock()
                self.__do_prevent_accidental_hard_drop()
                return
            
            if self.GameInstanceStruct.current_tetromino.max_moves_before_lock == 0 and self.GameInstanceStruct.current_tetromino.is_on_floor(): # if the piece has reached the maximum amount of moves lock it on contact with the floor
                self.__lock()
                self.__do_prevent_accidental_hard_drop()
                return
    
    # --------------------------------------------------- PREVENT ACCIDENTAL HARD DROP ---------------------------------------------------
                  
    def __do_prevent_accidental_hard_drop(self):
        """
        Set the prevent accidental hard drop flag if the setting is enabled
        """
        if self.Config.HANDLING_SETTINGS['PrevAccHD']:
            self.FlagStruct.DO_PREVENT_ACCIDENTAL_HARD_DROP = True
                    
    def __prevent_accidental_hard_drop(self):
        """
        Disable the hard drop action for a few ticks after a piece locks on its own to prevent accidental hard drops
        """
        if not self.FlagStruct.DO_PREVENT_ACCIDENTAL_HARD_DROP:
            return
        
        self.HandlingStruct.PREV_ACC_HD_COUNTER += 1
        
        if self.HandlingStruct.PREV_ACC_HD_COUNTER >= int(self.Config.HANDLING_SETTINGS['PrevAccHDTime']/60*self.Config.TPS):
            self.FlagStruct.DO_PREVENT_ACCIDENTAL_HARD_DROP = False
            self.HandlingStruct.PREV_ACC_HD_COUNTER = 0
            
    # --------------------------------------------------- EVENTS ---------------------------------------------------
    
    def __do_top_out_warning(self):
        """
        Activate the top out warning
        """
        if self.__is_row_17_empty():
            self.__event_danger(False)
        else:
            self.__get_next_piece_warn()
            self.__event_danger(True)
                
    def __is_row_17_empty(self):
        """
        Test if the 17th row is empty for top out warning
        """
        non_zero_idx = []
        for idx in self.GameInstanceStruct.matrix.matrix[22]:
            if idx != 0:
                non_zero_idx.append(idx)
                
        if len(non_zero_idx) != 0:
            return False
        else:
            return True
                         
    def __get_next_piece_warn(self):
        """
        Activate the top out warning
        """
        if self.FlagStruct.GAME_OVER:
            return
        
        next_piece = self.GameInstanceStruct.queue.view_queue(idx = 0)
        self.GameInstanceStruct.next_tetromino =  Tetromino(next_piece, 0, self.spawn_pos.x, self.spawn_pos.y , self.FlagStruct, self.GameInstanceStruct)
        
    def __event_danger(self, val:bool):
        """
        Toggle the danger flag
        
        args:
            val (bool): The value to set the danger flag to
        """
        if val:
            self.FlagStruct.DANGER = True
        else:
            self.FlagStruct.DANGER = False
    
    def reset_flags(self):
        self.FlagStruct.IS_SPIN = False
        self.FlagStruct_IS_MINI = False
        self.FlagStruct.LINE_CLEAR = False
        
    def __topout_ok_reset_game(self):
        self.FlagStruct.GAME_OVER = False
        self.GameInstanceStruct.reset = False
       
class Queue():
    def __init__(self, RNG, randomiser = '7BAG'):
        """
        Queue of next tetrominos
        
        args:
            rng (RNG): The random number generator to use
            randomiser (str): The randomiser type to use
        """
        self.RNG = RNG
        self.randomiser = randomiser
        
        if self.randomiser == '14BAG':
            self.tetrominos = ["Z", "L", "O", "S", "I", "J", "T", "Z", "L", "O", "S", "I", "J", "T"]
        else:
            self.tetrominos = ["Z", "L", "O", "S", "I", "J", "T"]
        
        self.length = len(self.tetrominos) * 3
        self.last_generated = None
        
        self.queue = []
        self.get_queue()

    def get_queue(self):
        """
        Fill the queue from the tetromino list and apply the relevant randomiser 
        """
        if self.randomiser == '7BAG' or self.randomiser == '14BAG':
            self.bag_randomiser()
                
        elif self.randomiser == 'CLASSIC':
            self.classic_randomiser()
        
        elif self.randomiser == 'PAIRS':
            self.pairs_randomiser()
        
        elif self.randomiser == 'RANDOM':
            self.random_randomiser()
            
    def get_next_piece(self):
        """
        Get the next piece from the queue and refill the queue as necessary.
        """
        next_piece = self.queue.pop(0)
        self.get_queue()
            
        return next_piece
    
    def view_queue(self, idx = 0):
        """
        See the next piece in the queue without removing it.
        """
        if idx < 0 or idx >= len(self.queue):
            return None
        return self.queue[idx]
    
    def bag_randomiser(self):
        """
        The 7-bag randomization system generates a set of the seven tetrominos and shuffles them before putting them into the queue.
        This guarantees that there will never be a gap of more than 12 tetrominos between any two tetrominos of the same type.
        
        The 14-bag randomization system is a variant of the 7-bag system with less of a guarantee against droughts.
        """
        while len(self.queue) <= self.length: 
            self.queue.extend(self.RNG.shuffle_array(self.tetrominos.copy())) 
    
    def classic_randomiser(self):
        """
        This is the randomizer used in Tetris for the NES. 
        For each piece, the randomizer rolls an eight-sided die, with seven sides representing seven tetrominos and the eighth side 
        representing a reroll. If a reroll or the same tetromino that was previously generated is rolled, 
        then the randomizer selects randomly from the tetrominos.
        """
        while len(self.queue) <= self.length:
                index = math.floor(self.RNG.next_float() * (len(self.tetrominos) + 1))
                if index == self.last_generated or index >= len(self.tetrominos):
                    index = math.floor(self.RNG.next_float() * len(self.tetrominos))
                self.last_generated = index
                self.queue.append(self.tetrominos[index]) 
    
    def pairs_randomiser(self):
        """
        This randomizer picks pairs of tetromino types and gives three of each in a random order.
        """
        while len(self.queue) <= self.length:
                s = self.RNG.shuffle_array(self.tetrominos.copy())
                pairs = [s[0], s[0], s[0], s[1], s[1], s[1]]
                self.queue.extend(self.RNG.shuffle_array(pairs))
               
    def random_randomiser(self):
        """
        This randomizer is entirely random.
        """
        while len(self.queue) < self.length:
                index = math.floor(self.RNG.next_float() * len(self.tetrominos))
                self.queue.append(self.tetrominos[index])

class RNG:
    def __init__(self, seed):
        """
        This pseudorandom number generator uses the Lehmer random number generator (specifically MINSTD) with the multiplier a = 16807 
        and the modulus m = 2147483647. It generates integers and floating-point numbers, and can also shuffle arrays.
        The shuffle algorithm is the Fisher–Yates shuffle.
        
        args:
            seed (int): The seed value for the RNG.
        """
        self.t = seed % 2147483647
        if self.t <= 0:
            self.t += 2147483646
    
    def next(self):
        """
        Generates the next pseudorandom integer in the sequence based on the current internal state.
        Uses the Lehmer random number generator
        
        returns:
            int: The next pseudorandom integer.
        """
        self.t = (16807 * self.t) % 2147483647
        return self.t

    def next_float(self):
        """
        Generates the next pseudorandom floating-point number in the range [0, 1) by converting
        the next integer from the Lehmer RNG into a floating-point number.
        
        returns:
            float: A pseudorandom floating-point number between 0 and 1.
        """
        return (self.next() - 1) / 2147483646

    def shuffle_array(self, array):
        """
        Shuffles the given array in place using the Fisher–Yates shuffle algorithm.
             
        args:
            array (list): The list to be shuffled.
        
        returns:
            list: The shuffled array.
        """
        if len(array) == 0:
            return array

        for i in range(len(array) - 1, 0, -1):
            r = math.floor(self.next_float() * (i + 1))
            [array[i], array[r]] = [array[r], array[i]]

        return array
        
      