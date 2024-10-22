from instance.tetromino import Tetromino
from instance.matrix import Matrix
from core.handling import Action
from instance.rotation import RotationSystem
import math
from utils import Vec2

class Four():
    def __init__(self, core_instance, matrix_width, matrix_height, rotation_system:str = 'SRS', randomiser = '7BAG', queue_previews = 5, seed = 0):
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
    
        self.rotation_system = RotationSystem(rotation_system)
        self.kick_table = self.rotation_system.kick_table
        
        self.GameInstanceStruct.randomiser = randomiser
        self.GameInstanceStruct.seed = seed
        self.GameInstanceStruct.queue_previews = queue_previews
        self.rng = RNG(self.GameInstanceStruct.seed)
        self.GameInstanceStruct.queue = Queue(self.rng, randomiser)
        self.GameInstanceStruct.matrix = Matrix(matrix_width, matrix_height)
    
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
            
            if self.__is_row_17_empty():
                self.__event_danger(False)
            else:
                self.__top_out_warn()
                self.__event_danger(True)

            self.__update_current_tetromino()
    
    def __update_current_tetromino(self):
        """
        Update the current tetromino at the end of the tick
        """
        if self.GameInstanceStruct.current_tetromino is None:
            return
        else:
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
        self.GameInstanceStruct.current_tetromino.rotate(action, self.kick_table['90'])
        
    def __rotate180(self, action):
        """
        Rotate the current tetromino by 180 degrees
        
        args:
            action (Action): The action to perform
        """
        self.GameInstanceStruct.current_tetromino.rotate(action, self.kick_table['180'])
  
    def __hard_drop(self):
        """
        Hard drop the current tetromino
        """
        self.__move_to_floor()
        self.__lock()
        
    def __soft_drop(self):
        """
        Soft drop the current tetromino
        """
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
        if self.GameInstanceStruct.current_tetromino is not None:
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
        self.GameInstanceStruct.matrix.clear_lines()
        # TODO: Implement scoring logic / t spin line clear detection
    
    # --------------------------------------------------- GRAVITY ---------------------------------------------------
    
    def __perform_gravity(self):
        """
        Perform gravity on the current tetromino
        """               
        for action_dict in self.actions_this_tick:
            action = action_dict['action']
            
            if action == Action.SOFT_DROP:
                self.__soft_drop()
            
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
        
        spawning_tetromino = Tetromino(next_piece, 0,  self.spawn_pos.x,  self.spawn_pos.y, self.GameInstanceStruct.matrix, self.FlagStruct)
        self.GameInstanceStruct.lock_delay_counter = 0
        
        if hold_spawn == 'swap': # if the piece is being swapped in, insert the blocks before checking if it can spawn (visual consistency otherwise will look like you die for no reason)
            self.GameInstanceStruct.current_tetromino = None
            self.GameInstanceStruct.current_tetromino = spawning_tetromino
            self.__check_spawn(spawning_tetromino)
        
        elif hold_spawn == 'hold': # if the current piece is being held, normal behaviour
            self.GameInstanceStruct.current_tetromino = None
            if self.__check_spawn(spawning_tetromino):
                self.GameInstanceStruct.queue.get_next_piece()
                self.GameInstanceStruct.current_tetromino = spawning_tetromino
        else:
            self.GameInstanceStruct.current_tetromino = None
            if self.__check_spawn(spawning_tetromino):
                self.GameInstanceStruct.queue.get_next_piece()
                self.GameInstanceStruct.current_tetromino = spawning_tetromino
    
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
                         
    def __top_out_warn(self):
        """
        Activate the top out warning
        """
        if self.FlagStruct.GAME_OVER:
            return
        
        next_piece = self.GameInstanceStruct.queue.view_queue(idx = 0)
        self.GameInstanceStruct.next_tetromino =  Tetromino(next_piece, 0, self.spawn_pos.x, self.spawn_pos.y , self.GameInstanceStruct.matrix, self.FlagStruct)
        
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
    
class Queue():
    def __init__(self, rng, randomiser = '7BAG'):
        """
        Queue of next tetrominos
        
        args:
            rng (RNG): The random number generator to use
            length (int): The length of the queue
        """
        self.randomiser = randomiser
        self.minos = ["Z", "L", "O", "S", "I", "J", "T"]
        
        if self.randomiser == '14BAG':
            self.minos = ["Z", "L", "O", "S", "I", "J", "T", "Z", "L", "O", "S", "I", "J", "T"]
        
        self.length = len(self.minos) * 2
        self.rng = rng
        self.length = 14
        self.bag = self.get_bag() if self.randomiser in ['7BAG', '14BAG'] else None
        self.last_generated = None
        
        self.queue = []
        self.get_queue()

    def get_bag(self):
        """
        Create and shuffle a new bag of seven tetrominos
        """
        return self.rng.shuffle_array(self.minos.copy()) 

    def get_queue(self):
        """
        Fill the queue from the bag, and refill the bag when empty.
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
        while len(self.queue) <  self.length:
                if len(self.bag) == 0: 
                    self.bag = self.get_bag()
                self.queue.append(self.bag.pop(0)) 
    
    def classic_randomiser(self):
        while len(self.queue) < self.length:
                index = math.floor(self.rng.next_float() * (len(self.minos) + 1))
                if index == self.last_generated or index >= len(self.minos):
                    index = math.floor(self.rng.next_float() * len(self.minos))
                self.last_generated = index
                self.queue.append(self.minos[index]) 
    
    def pairs_randomiser(self):
        while len(self.queue) < self.length:
                s = self.rng.shuffle_array(self.minos.copy())
                pairs = [s[0], s[0], s[0], s[1], s[1], s[1]]
                self.queue.extend(self.rng.shuffle_array(pairs))
               
    def random_randomiser(self):
        while len(self.queue) < self.length:
                index = math.floor(self.rng.next_float() * len(self.minos))
                self.queue.append(self.minos[index])

class RNG:
    def __init__(self, seed):
        self.t = seed % 2147483647
        if self.t <= 0:
            self.t += 2147483646
    
    def next(self):
        self.t = (16807 * self.t) % 2147483647
        return self.t

    def next_float(self):
        return (self.next() - 1) / 2147483646

    def shuffle_array(self, array):
        if len(array) == 0:
            return array

        for i in range(len(array) - 1, 0, -1):
            r = math.floor(self.next_float() * (i + 1))
            [array[i], array[r]] = [array[r], array[i]]

        return array
        
      