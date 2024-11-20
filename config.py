from dataclasses import dataclass

@dataclass
class StructConfig():

    UNCAPPED_FPS: bool = True
    FPS: int = 144
    TPS: int = 256
    POLLING_RATE: int = 1000
    
    CAPTION = 'Four'
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900