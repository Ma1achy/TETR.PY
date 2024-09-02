from tetromino import Tetromino
from matrix import Matrix
from config import Config
from render import Render
from handling import Action

class Four():
    def __init__(self, pygame_instance):
        """
        Create an instance of the game Four
        """
        self.pygame_instance = pygame_instance
        self.config = Config()
        self.render = Render(self.pygame_instance.window)
       
        self.rng = self.__init_rng()
        self.queue = self.__init_queue()
        self.matrix = self.__init_matrix()
        
        self.held_tetromino = None 
        self.current_tetromino = None
        
    def loop(self):
        """
        The main game loop
        """
        actions = self.pygame_instance.before_loop_hook()
        
        for action in actions:
            if actions[action]:
                print(action)
          
        self.render.render_frame(self)  
        self.__get_next_state(actions)
        
    def __get_next_state(self, actions):
        """
        Get the next state of the game
        """
        
        self.__perform_actions(actions)
        pass
    
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
    
    def __spawn_piece(self):
        """
        Spawn a new tetromino
        """
        # function as of now is like this for testing, need to instead try spawn a piece above the field in the piece spawning bounding box
        # inside this box the piece will attempt to spawn such that it doesnt collide with any occupied cells. if it fails -> game over
        self.current_tetromino = Tetromino(self.queue.get_next_piece(), 0, 4, 18, self.matrix)
        self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
    
    def __hard_drop(self):
        pass
    
    def __hold(self):
        pass
    
    def __update_current_tetromino(self):
        self.matrix.piece = self.matrix.empty_matrix()
        self.matrix.insert_blocks(self.current_tetromino.blocks, self.current_tetromino.position, self.matrix.piece)
        self.current_tetromino.ghost()
        
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
                    else: # buffer the action to be performed when a tetromino is spawned
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