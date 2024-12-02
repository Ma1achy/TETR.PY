from dataclasses import dataclass

@dataclass
class StructConfig():

    UNCAPPED_FPS: bool = True
    FPS: int = 144
    TPS: int = 256
    POLLING_RATE: int = 1000
    
    VERSION = 'alpha 0.1'