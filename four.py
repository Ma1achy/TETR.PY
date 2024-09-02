# from tetromino import Tetromino
from matrix import Matrix
from config import Config
from handling import Action

class Four():
    def __init__(self, config):
        """
        Create an instance of the game Four
        """
        self.config = config
       
        self.rng = self.__init_rng()
        self.queue = self.__init_queue()
        self.matrix = self.__init_matrix()
        self.held_tetromino = None 
        self.current_tetromino = None
        
    def loop(self):
        """
        The main game loop
        """
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
        pass
    
    def __handle_actions(self, actions):
        for action in actions:
            match action:
                case Action.MOVE_LEFT:
                    self.current_tetromino.move('LEFT')
                    
                case Action.MOVE_RIGHT:
                    self.current_tetromino.move('RIGHT')
                    
                case Action.ROTATE_CLOCKWISE:
                    self.current_tetromino.rotate('CW')
                    
                case Action.ROTATE_COUNTERCLOCKWISE:
                    self.current_tetromino.rotate('CCW')
                    
                case Action.HARD_DROP:
                    pass
                    
                case Action.SOFT_DROP:
                    self.current_tetromino.move('DOWN')
                case Action.HOLD:
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

four = Four(Config)
# rng = RNG(seed = 0)
# Q = Queue(rng, length = 5)

# for i in range(100):
#     next_piece = Q.get_next_piece()
#     print(f'queue: {Q.queue}')
#     print(f'next: {next_piece}')