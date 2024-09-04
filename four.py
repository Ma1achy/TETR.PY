from tetromino import Tetromino
from matrix import Matrix
from config import Config
from render import Render
from handling import Action
import pygame

class Four():
    def __init__(self, pygame_instance):
        """
        Create an instance of the game Four
        
        args:
        pygame_instance (PyGameInstance): The pygame instance to use
        """
        self.pygame_instance = pygame_instance
        self.config = Config()
       
        self.rng = self.__init_rng()
        self.queue = self.__init_queue()
        self.matrix = self.__init_matrix()
        
        self.held_tetromino = None 
        self.current_tetromino = None
        self.game_over = False
        self.danger = True
        self.game_clock = pygame.time.Clock()
        
    def loop(self):
        """
        The main game loop
        
        args:
        dt (float): The time since the last frame
        """
        actions = self.pygame_instance.before_loop_hook()
        self.__get_next_state(actions)
        self.game_clock.tick()
        
    def __get_next_state(self, actions):
        """
        Get the next state of the game
        """
        if not self.game_over:
            self.__perform_actions(actions)
            self.__update_current_tetromino()
            
            if self.current_tetromino is None:
                self.__get_next_piece(hold = False)
            
            if self.__is_row_17_empty():
                self.__event_danger(False)
            else:
                self.__top_out_warn()
                self.__event_danger(True)
                
            self.__clear_lines()
        
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
        if self.current_tetromino is not None:
            self.matrix.piece = self.matrix.empty_matrix()
            self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
            self.current_tetromino.ghost()
        
    def __get_next_piece(self, hold):
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
            
    def __spawn_piece(self, next_piece):
        """
        Spawn a new tetromino
        """
        spawning_tetromino = Tetromino(next_piece, 0, 4, 18, self.matrix)
        
        if self.__check_spawn(spawning_tetromino):
            self.current_tetromino = spawning_tetromino
            self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
            self.__update_current_tetromino()
        else:
            self.game_over = True
            print("Game Over")
            
        self.__update_current_tetromino()
    
    def __check_spawn(self, spawning_tetromino):
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
        if self.can_hold:
            self.__get_next_piece(hold = True)
        
    def __perform_actions(self, actions):
        pass
        for action, is_action in actions.items():
            if not is_action:
                continue
            
            match action:
                case Action.MOVE_LEFT:
                    if self.current_tetromino is not None: 
                        self.current_tetromino.move('LEFT') 
                        self.__update_current_tetromino()
                    else: 
                        pass
                    
                case Action.MOVE_RIGHT:
                    if self.current_tetromino is not None:
                        self.current_tetromino.move('RIGHT')
                        self.__update_current_tetromino()
                    else:
                        pass
                    
                case Action.ROTATE_CLOCKWISE:
                    if self.current_tetromino is not None:
                        self.current_tetromino.rotate('CW')
                        self.__update_current_tetromino()
                    else:
                        pass
                    
                case Action.ROTATE_COUNTERCLOCKWISE:
                    if self.current_tetromino is not None:
                        self.current_tetromino.rotate('CCW')
                        self.__update_current_tetromino()
                    else:
                        pass
                    
                case Action.ROTATE_180:
                    if self.current_tetromino is not None:
                        self.current_tetromino.rotate('180')
                        self.__update_current_tetromino()
                    else:
                        pass
                    
                case Action.HARD_DROP:
                    if self.current_tetromino is not None:
                        self.__hard_drop()
                    pass
                    
                case Action.SOFT_DROP:
                    if self.current_tetromino is not None:
                        self.current_tetromino.move('DOWN')
                        self.__update_current_tetromino()
                        
                case Action.HOLD:
                    if self.current_tetromino is not None:
                        self.__hold()
                        pass
                    else:
                        pass
                    pass
    def __is_row_17_empty(self):
        non_zero_idx = []
        for idx in self.matrix.matrix[22]:
            if idx != 0:
                non_zero_idx.append(idx)
                
        if len(non_zero_idx) != 0:
            return False
        else:
            return True
                         
    def __top_out_warn(self):
        
        if self.game_over:
            return
        
        next_piece = self.queue.view_queue(idx = 0)
        danger = Tetromino(next_piece, 0, 4, 18, self.matrix)
        
        self.matrix.danger = self.matrix.empty_matrix()
        danger.blocks = [tuple(-1 if val != 0 else val for val in row) for row in danger.blocks]
        self.matrix.insert_blocks(danger.blocks, danger.position, self.matrix.danger)
        
    def __event_danger(self, val):
        if val:
            self.danger = True
        else:
            self.danger = False

class Queue():
    def __init__(self, rng, length = 5):
        """
        Queue of next tetrominos
        
        args:
        seed (int): The seed to use for the random number generator
        length (int): The length of the queue
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