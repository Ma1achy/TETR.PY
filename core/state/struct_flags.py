from dataclasses import dataclass

@dataclass
class StructFlags():

    danger: bool = False
    game_over: bool = False