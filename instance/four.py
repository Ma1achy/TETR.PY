from instance.tetromino import Tetromino
from instance.matrix import Matrix
from config import Config
from core.handling import Action
from instance.rotation import RotationSystem
from utils import Vec2
import math
class Four():
    def __init__(self, core_instance, rotation_system = 'SRS'):
        """
        Create an instance of the game Four
        
        args:
            core (Core): The core instance of the game
            rotation_system (str): The rotation system to use
            
        methods:
            loop(): The main game loop
            forward_state(): Forward the state of the game to allow for async rendering
        """
        self.core_instance = core_instance
        self.config = Config() 
        self.spawn_pos = Vec2(4, 18)
       
        self.rotation_system = RotationSystem(rotation_system)
        self.kick_table = self.rotation_system.kick_table
        self.rng = self.__init_rng()
        self.queue = self.__init_queue()
        self.matrix = self.__init_matrix()
                
        self.held_tetromino = None 
        self.current_tetromino = None
        self.game_over = False
        self.danger = False
        
        self.current_time = 0
        self.previous_time = 0

        self.soft_dropping = True
        self.soft_drop_factor = 1
        self.gravity_counter = 0
        self.gravity = 1/60
        self.move_down = False
        self.G_units_in_ticks = 0
        
        self.on_floor = False
        
    def loop(self, current_time, previous_time):
        """
        The main game loop
        
        args:
            current_time (int): The current time in seconds
        """
        self.current_time = current_time
        self.previous_time = previous_time
        self.soft_drop_factor = 1
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
            tick_duration = 1000/ self.config.TPS
            
        for action_dict in list(self.core_instance.handling.action_queue):
           
            relative_tick = int((action_dict['timestamp'] - self.core_instance.current_time) / tick_duration)
                 
            if relative_tick <= 0 and abs(relative_tick) <= self.core_instance.handling.buffer_threshold: # only perform past actions that haven't been performed that are within the buffer threshold or actions that are on this tick
                self.actions_this_tick.append(action_dict)
                self.core_instance.handling.consume_action()
        
    def forward_state(self):
        """
        Forward the state of the game to allow for async rendering.
        """
        return StateSnapshot(self)
        
    def __get_next_state(self):
        """
        Get the next state of the game
        """
        if not self.game_over:
            self.__perform_actions()
            self.__do_gravity(self.gravity, self.soft_drop_factor)
            self.__update_current_tetromino()
            self.__clear_lines()
            
            if self.current_tetromino is None:
                self.__get_next_piece(hold = False)
            
            if self.__is_row_17_empty():
                self.__event_danger(False)
            else:
                self.__top_out_warn()
                self.__event_danger(True)
                
    def __init_rng(self):
        """
        Create a random number generator
        """
        return RNG(self.config.SEED)
    
    def __init_queue(self):
        """
        Create a queue of tetrominos
        """
        return Queue(self.rng, self.config.QUEUE_LENGTH)
    
    def __init_matrix(self):
        """
        Create the game field
        """
        return Matrix(self.config.MATRIX_WIDTH, self.config.MATRIX_HEIGHT)
    
    def __update_current_tetromino(self):
        """
        Update the current tetromino in the matrix
        """
        
        if self.current_tetromino is not None:
            self.matrix.piece = self.matrix.empty_matrix()
            self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
            self.current_tetromino.ghost()
            self.on_floor = self.current_tetromino.is_on_floor()
        
    def __get_next_piece(self, hold:bool):
        """
        Get the next piece from the queue and spawn it
        
        args:
            hold (bool): Whether to hold the current piece
        """
        self.can_hold = True
        
        if hold is False:
            next_piece = self.queue.get_next_piece()
        else:
            if self.held_tetromino is not None:
                next_piece = self.held_tetromino
                self.held_tetromino = self.current_tetromino.type
                self.can_hold = False
            else:
                next_piece = self.queue.get_next_piece()
                self.held_tetromino = self.current_tetromino.type
                self.can_hold = False
                
        self.__spawn_piece(next_piece)
            
    def __spawn_piece(self, next_piece:str):
        """
        Spawn a new tetromino
        
        args:
            next_piece (str): The type of the next tetromino
        """
        spawning_tetromino = Tetromino(next_piece, 0, self.spawn_pos.x, self.spawn_pos.y, self.matrix)
        
        if self.__check_spawn(spawning_tetromino):
            self.current_tetromino = spawning_tetromino
            self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
            self.__update_current_tetromino()
        else:
            self.game_over = True
            print("Game Over")
            
        self.__update_current_tetromino()
    
    def __check_spawn(self, spawning_tetromino):
        """
        Check if the tetromino can spawn in the matrix
        """
        if not spawning_tetromino.collision(spawning_tetromino.blocks, spawning_tetromino.position):
            return True
    
    def __clear_lines(self):
        """
        Clear full lines from the matrix
        """
        cleared_lines = self.matrix.clear_lines()
        # TODO: Implement scoring logic / t spin line clear detection
        
    def __hard_drop(self):
        """
        Hard drop the current tetromino
        """
        self.current_tetromino.position = self.current_tetromino.ghost_position
        self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.matrix)
        self.matrix.piece = self.matrix.empty_matrix()
        self.current_tetromino = None
    
    def __hold(self):
        """
        Hold the current tetromino
        """
        if self.can_hold:
            self.__get_next_piece(hold = True)
        
    def __perform_actions(self):
        
        for action_dict in self.actions_this_tick:
            action = action_dict['action'] 
            
            match action:
                case Action.MOVE_LEFT | Action.MOVE_RIGHT:
                    if self.current_tetromino is not None: 
                        self.current_tetromino.move(action) 
                        self.__update_current_tetromino()
                    
                case Action.ROTATE_CLOCKWISE | Action.ROTATE_COUNTERCLOCKWISE:
                    if self.current_tetromino is not None:
                        self.current_tetromino.rotate(action, self.kick_table['90'])
                        self.__update_current_tetromino()
                
                case Action.ROTATE_180:
                    if self.current_tetromino is not None:
                        self.current_tetromino.rotate(action, self.kick_table['180'])
                        self.__update_current_tetromino()
                    
                case Action.HARD_DROP:
                    if self.current_tetromino is not None:
                        self.__hard_drop()
                    
                case Action.SOFT_DROP:  
                    if self.current_tetromino is not None:
                        self.soft_drop_factor = self.config.HANDLING_SETTINGS['SDF']
                        self.__update_current_tetromino()
                        
                case Action.HOLD:
                    if self.current_tetromino is not None:
                        self.__hold()
                
    def __is_row_17_empty(self):
        """
        Test if the 17th row is empty for top out warning
        """
        non_zero_idx = []
        for idx in self.matrix.matrix[22]:
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
        if self.game_over:
            return
        
        next_piece = self.queue.view_queue(idx = 0)
        danger = Tetromino(next_piece, 0, 4, 18, self.matrix)
        
        self.matrix.danger = self.matrix.empty_matrix()
        danger.blocks = [tuple(-1 if val != 0 else val for val in row) for row in danger.blocks]
        self.matrix.insert_blocks(danger.blocks, danger.position, self.matrix.danger)
        
    def __event_danger(self, val:bool):
        """
        Toggle the danger flag
        
        args:
            val (bool): The value to set the danger flag to
        """
        if val:
            self.danger = True
        else:
            self.danger = False
            
    def __do_gravity(self, G, soft_drop_factor = 1):
        """
        Perform gravity
        
        args:
            G (int): The gravity value in blocks per fractions of 1/60th of a second, i.e 1G = 1 block per 1/60th of a second
        """
        self.__reset_gravity_after_soft_drop()
        
        if soft_drop_factor == 'inf':
            self.__move_to_floor()
                
        if G == 0 or self.current_tetromino is None or self.current_tetromino.is_on_floor():
            self.gravity_counter = 0
            return
        
        elif G == 20:
            self.__move_to_floor()
        else:
            # convert G from units blocks per 1/60 seconds to units blocks per no. of ticks 
            self.G_units_in_ticks = self.config.TPS/((G * soft_drop_factor) * 60)
            
            if self.gravity_counter >= int(self.G_units_in_ticks):
                self.__gravity_tick()
            else:
                self.gravity_counter += 1
        
    def __gravity_tick(self):
        """
        Gravity tick
        """
        self.current_tetromino.attempt_to_move_downwards()
        self.gravity_counter = 0
        
    def __move_to_floor(self):
        """
        Move the current tetromino to the floor
        """
        while not self.current_tetromino.is_on_floor():
            self.current_tetromino.attempt_to_move_downwards()
            
    def __reset_gravity_after_soft_drop(self):
        """
        Reset the gravity counter after a soft drop so there is no extra time left on the gravity counter
        """
        for ac in self.actions_this_tick:
            if Action.SOFT_DROP not in ac.values():
                self.gravity_counter = 0
                break
                
class Queue():
    def __init__(self, rng, length = 5):
        """
        Queue of next tetrominos
        
        args:
            rng (RNG): The random number generator to use
            length (int): The length of the queue
            
        methods:
            get_bag(): Create a bag of tetrominos
            get_queue(): Get the queue of tetrominos
            get_next_piece(): Get the next piece from the queue
            view_queue(): See a piece in the queue at a specific index
        """
        self.rng = rng
        self.length = length
        self.bag = self.get_bag()
        self.queue = []
        self.get_queue()
 
    def get_bag(self):
        """
        Create a bag of seven tetrominos
        
        args:
            bag (list): The bag to fill with tetrominos
        """
        bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
        self.rng.shuffle_array(bag)
        
        return bag
    
    def get_queue(self):
        """
        Take a piece from the bag without replacement and add it to the queue if the bag is empty refill the bag
        """
        while len(self.queue) < self.length:
            
            if len(self.bag) == 0:
                self.bag = self.get_bag()
                
            self.queue.append(self.bag.pop())
            
    def get_next_piece(self):
        """
        Get the next piece from the queue
        """
        next_piece = self.queue.pop(0)
        
        if len(self.queue) < self.length:
            self.get_queue()
            
        return next_piece
    
    def view_queue(self, idx = 0):
        """
        See the next piece in the queue
        """
        if idx >= len(self.queue) - 1:
            return self.queue[-1]
        return self.queue[idx]

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
            r = int(self.next_float() * (i + 1))
            array[i], array[r] = array[r], array[i]

        return array
    
class StateSnapshot:
    def __init__(self, four_instance):
        """
        Initialize the state snapshot with the relevant game state.
        
        Args:
            four_instance (Four): The instance of the game from which to copy the state.
        """
        self.current_tetromino = four_instance.current_tetromino
        self.matrix = four_instance.matrix
        self.queue = four_instance.queue
        self.held_tetromino = four_instance.held_tetromino
        self.game_over = four_instance.game_over
        self.danger = four_instance.danger
        
        self.gravity = four_instance.gravity
        self.gravity_counter = four_instance.gravity_counter
        self.soft_drop_factor = four_instance.soft_drop_factor
        self.G_units_in_ticks = four_instance.G_units_in_ticks
        self.on_floor = four_instance.on_floor
        self.soft_drop_factor = four_instance.soft_drop_factor