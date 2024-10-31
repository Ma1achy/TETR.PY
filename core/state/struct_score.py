from dataclasses import dataclass

@dataclass
class StructScore:
        lines_cleared: int = None
        cleared_blocks: int = None
        cleared_idxs: int = None
        
        is_spin: int = None
        is_mini: int = None
