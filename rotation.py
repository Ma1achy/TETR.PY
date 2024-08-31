from vec2 import Vec2

TSZLJ_OFFSETS = ([                                                      
    ([Vec2(0, 0), Vec2(0, 0),  Vec2(0, 0),   Vec2(0, 0), Vec2(0, 0)]),  
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(1, -1),  Vec2(0, 2), Vec2(1, 2)]),  
    ([Vec2(0, 0), Vec2(0, 0),  Vec2(0, 0),   Vec2(0, 0), Vec2(0, 0)]),  
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-1, -1), Vec2(0, 2), Vec2(-1, 2)]), 
])

I_OFFSETS = ([ 
    ([Vec2(0, 0),  Vec2(-1, 0), Vec2(2, 0),  Vec2(-1, 0), Vec2(2, 0)]),
    ([Vec2(-1, 0), Vec2(0, 0),  Vec2(0, 0),  Vec2(0, 1),  Vec2(0, -2)]),
    ([Vec2(-1, 1), Vec2(1, 1),  Vec2(-2, 1), Vec2(1, 0),  Vec2(-2, 0)]),
    ([Vec2(0, 1),  Vec2(0, 1),  Vec2(0, 1),  Vec2(0, -1), Vec2(0, 2)]),
])

O_OFFSETS = ([ # technically in SRS O actually has non zero offsets here but they only exist because for some reason standard tetris doesn't make the O piece a 2x2 array so it has to be kicked every time it rotates???
    [(Vec2(0, 0))],
    [(Vec2(0, 0))],
    [(Vec2(0, 0))],
    [(Vec2(0, 0))],
])

TSZLKJ_180_OFFSETS = ([
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, 1),   Vec2(2, 1),   Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, 1),  Vec2(-2, 1),  Vec2(0, -1), Vec2(3, 0),  Vec2(-3, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(-1, 1),  Vec2(-1, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, -1), Vec2(-1, -2), Vec2(1, 0),  Vec2(0, 3),  Vec2(0, -3)]),
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, -1), Vec2(-2, -1), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, -1),  Vec2(2, -1),  Vec2(0, 1),  Vec2(-3, 0), Vec2(3, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(1, 1),   Vec2(1, 2),   Vec2(0, -1), Vec2(0, -2), Vec2(1, -1),  Vec2(1, -2),  Vec2(-1, 0), Vec2(0, 3),  Vec2(0, -3)])
])

I_180_OFFSETS = (
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(0, 1),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(-1, 0), Vec2(-2, 0), Vec2(0, -1), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(1, 0),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)])
)

def get_kick(rotation:str, piece:str, initial_state:int, desired_state:int, offset_order:int):
    """
    Get the kick translation to apply to the piece
    kick = initial_state_offset - desired_state_offset
    
    args:
    rotation (str): Rotation direction: ['CW', 'CCW', '180']
    piece (str): Type of the piece: ['T', 'S', 'Z', 'L', 'J', 'I', 'O']
    initial_state (int): Initial rotation state of the piece: [0, 1, 2, 3]
    desired_state (int): Desired rotation state of the piece: [0, 1, 2, 3]
    offset_order (int): Offset order to use 
    
    returns:
    kick (Vec2): The kick translation to apply to the piece
    """
    if rotation in ['CW', 'CCW']:
        if piece in ['T', 'S', 'Z', 'L', 'J']:
            
            if offset_order > len(TSZLJ_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = TSZLJ_OFFSETS[desired_state][offset_order]
                initial_state_offset = TSZLJ_OFFSETS[initial_state][offset_order]
            
        elif piece == 'O':
            
            if offset_order > len(O_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = O_OFFSETS[desired_state][offset_order]
                initial_state_offset = O_OFFSETS[initial_state][offset_order]
            
        elif piece == 'I':
            
            if offset_order > len(I_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = I_OFFSETS[desired_state][offset_order]
                initial_state_offset = I_OFFSETS[initial_state][offset_order]
            
    elif rotation == '180':
        if piece in ['T', 'S', 'Z', 'L', 'J']:
            
            if offset_order > len(TSZLKJ_180_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = TSZLKJ_180_OFFSETS[desired_state][offset_order]
                initial_state_offset = TSZLKJ_180_OFFSETS[initial_state][offset_order]
            
        elif piece == 'O':
            
            if offset_order > len(O_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = O_OFFSETS[desired_state][offset_order]
                initial_state_offset = O_OFFSETS[initial_state][offset_order]
            
        elif piece == 'I':
            
            if offset_order > len(I_180_OFFSETS[0]) - 1:
                return None
            else:
                desired_state_offset = I_180_OFFSETS[desired_state][offset_order]
                initial_state_offset = I_180_OFFSETS[initial_state][offset_order]
                
    return initial_state_offset - desired_state_offset
        
def pieces(piece:str):
    """
    Get the blocks for the given piece.
    This is the 0th rotation state of the piece that SRS uses.
    
    returns:
    blocks (list): The pieces blocks
    """
    blocks = {
        'T':
            [
                (0, 1, 0),
                (1, 1, 1),
                (0, 0, 0)
            ],
        'S': 
            [
                (0, 2, 2),
                (2, 2, 0),
                (0, 0, 0)
            ],
            
        'Z':
            [
                (3, 3, 0),
                (0, 3, 3),
                (0, 0, 0)
            ],
        'L': 
            [
                (0, 0, 4),
                (4, 4, 4),
                (0, 0, 0)
            ],
        'J':
            [
                (5, 0, 0),
                (5, 5, 5),
                (0, 0, 0)
            ],
        'O': # easier to make O 2x2 and consider it seperately like I rather than make it 3x3 and have to kick it every time it rotates
            [
                (6, 6), 
                (6, 6),
            ],
        'I': 
            [
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0),
                (0, 7, 7, 7, 7),
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0)
            ] 
    }
    return blocks[piece]