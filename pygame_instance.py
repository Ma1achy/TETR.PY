from matrix import Matrix
import pygame
from pygame_config import PyGameConfig
from config import Config
from render import Render
from tetromino import Tetromino

# TODO: IMPLEMENT BASIC INPUT HANDLING AGAIN

class PyGameInstance():
    def __init__(self):
        
        pygame.init()
        self.config = PyGameConfig
        self.window = self.__init_window()
        
    def __init_window(self):
        """
        Create the window
        """
        pygame.display.set_caption(self.config.CAPTION)
        return pygame.display.set_mode((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.DOUBLEBUF)
     
    def play_sound(self, sound:str):
        match sound:
            case 'hard drop':
                pass
            case 'lock':
                pass
            case 'single':
                pass
            case 'double':
                pass	
            case 'triple':
                pass
            case 'quadruple':
                pass
            case 't spin':
                pygame.mixer.music.load("SE/t_spin.wav")
                pygame.mixer.music.set_volume(0.20)
                pygame.mixer.music.play()
            case 'hold':
                pass
            case 'pre-rotate':
                pass
            case 'slide left':
                pass
            case 'slide right':
                pass
            case 'warning':
                pass

# testing 
matrix = Matrix(Config.MATRIX_WIDTH, Config.MATRIX_HEIGHT)
tetromino = Tetromino('T', 0, 4, 18, matrix)
matrix.insert_blocks(tetromino.blocks, tetromino.position, matrix.piece)

pygame_instance = PyGameInstance()
render = Render(pygame_instance.window)

while True:
    render.render_frame(matrix)
    tetromino.ghost()
