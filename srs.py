from maths import Vec2

# define the offsets to use when applying a kick to a piece.

cw_rotation_data = ([
    Vec2(0, -1), 
    Vec2(1, 0),
])

ccw_rotation_data = ([
    Vec2(0, 1),
    Vec2(-1, 0),
])

# when rotating from A to B, B - A gives the kick translation to apply to the piece
# the offsets are applied in order, so the 0th is applied first, then the 1st, 2nd, etc.
# row = offset order, column = rotation state

# 90 degree rotation offsets
    # offset 0    offset 1     offset 2     offset 3    offset 4 
TSZLJ_OFFSETS = ([                                                      # rotation state
    ([Vec2(0, 0), Vec2(0, 0),  Vec2(0, 0),   Vec2(0, 0), Vec2(0, 0)]),  # 0
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(1, -1),  Vec2(0, 2), Vec2(1, 2)]),  # 1
    ([Vec2(0, 0), Vec2(0, 0),  Vec2(0, 0),   Vec2(0, 0), Vec2(0, 0)]),  # 2
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-1, -1), Vec2(0, 2), Vec2(-1, 2)]), # 3
])

I_OFFSETS = ([ 
    ([Vec2(0, 0),  Vec2(-1, 0), Vec2(2, 0),  Vec2(-1, 0), Vec2(2, 0)]),
    ([Vec2(-1, 0), Vec2(0, 0),  Vec2(0, 0),  Vec2(0, 1),  Vec2(0, -2)]),
    ([Vec2(-1, 1), Vec2(1, 1),  Vec2(-2, 1), Vec2(1, 0),  Vec2(-2, 0)]),
    ([Vec2(0, 1),  Vec2(0, 1),  Vec2(0, 1),  Vec2(0, -1), Vec2(0, 2)]),
])

O_OFFSETS = ([
    [(Vec2(0, 0))],
    [(Vec2(0, -1))],
    [(Vec2(-1, -1))],
    [(Vec2(-1, 0))],
])

# 180 degree rotation offsets

TSZLKJ_180_OFFSETS = ([
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, 1),   Vec2(2, 1),   Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, 1),  Vec2(-2, 1),  Vec2(0, -1), Vec2(3, 0),  Vec2(-3, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(-1, 1),  Vec2(-1, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, -1), Vec2(-1, -2), Vec2(1, 0),  Vec2(0, 3),  Vec2(0, -3)]),
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, -1), Vec2(-2, -1), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, -1),  Vec2(2, -1),  Vec2(0, 1),  Vec2(-3, 0), Vec2(3, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(1, 1),   Vec2(1, 2),   Vec2(0, -1), Vec2(0, -2), Vec2(1, -1),  Vec2(1, -2),  Vec2(-1, 0), Vec2(0, 3),  Vec2(0, -3)])
])

I_180_OFFSETS = ([
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(0, 1),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(-1, 0), Vec2(-2, 0), Vec2(0, -1), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(1, 0),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)])
])

def get_rotation_state(piece:str, state:int):
    """	
    Get the rotation state of a piece
    
    args:
    piece (str): Type of the piece S, Z, J, L, I, T, O
    state (int): Rotation state of the piece 0, 1, 2, 3
    
    returns:
    (list): The rotation state of the piece
    """
    blocks = {
        'T': { 
            0: [
                (0, 1, 0),
                (1, 1, 1),
                (0, 0, 0)
                ],
            1: [
                (0, 1, 0),
                (0, 1, 1),
                (0, 1, 0)
            ],
            2: [
                (0, 0, 0),
                (1, 1, 1),
                (0, 1, 0)
                ],
            3: [
                (0, 1, 0),
                (1, 1, 0),
                (0, 1, 0)
                ]
        },
        'S': {
            0: [
                (0, 2, 2),
                (2, 2, 0),
                (0, 0, 0)
            ],
            1: [
                (0, 2, 0),
                (0, 2, 2),
                (0, 0, 2)
            ],
            2: [
                (0, 0, 0),
                (0, 2, 2),
                (2, 2, 0)
            ],
            3: [
                (2, 0, 0),
                (2, 2, 0),
                (0, 2, 0)
            ]
        },
        'Z': {
            0: [
                (3, 3, 0),
                (0, 3, 3),
                (0, 0, 0)
            ],
            1: [
                (0, 0, 3),
                (0, 3, 3),
                (0, 3, 0)
            ],
            2: [
                (0, 0, 0),
                (3, 3, 0),
                (0, 3, 3)
            ],
            3: [
                (0, 3, 0),
                (3, 3, 0),
                (3, 0, 0)
            ]
        },
        'L': {
            0: [
                (0, 0, 4),
                (4, 4, 4),
                (0, 0, 0)
            ],
            1: [
                (0, 4, 0),
                (0, 4, 0),
                (0, 4, 4)
            ],
            2: [
                (0, 0, 0),
                (4, 4, 4),
                (4, 0, 0)
            ],
            3: [
                (4, 4, 0),
                (0, 4, 0),
                (0, 4, 0)
            ]
        },
        'J': {
            0: [
                (5, 0, 0),
                (5, 5, 5),
                (0, 0, 0)
            ],
            1: [
                (0, 5, 5),
                (0, 5, 0),
                (0, 5, 0)
            ],
            2: [
                (0, 0, 0),
                (5, 5, 5),
                (0, 0, 5)
            ],
            3: [
                (0, 5, 0),
                (0, 5, 0),
                (5, 5, 0)
            ]
        },
        'O': {
            0: [
                (0, 6, 6),
                (0, 6, 6),
                (0, 0, 0)
            ],
            1: [
                (0, 0, 0),
                (0, 6, 6),
                (0, 6, 6)
            ],
            2: [
                (0, 0, 0),
                (6, 6, 0),
                (6, 6, 0)
            ],
            3: [
                (6, 6, 0),
                (6, 6, 0),
                (0, 0, 0)
            ]
        },
        'I': {
            0: [
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0),
                (0, 7, 7, 7, 7),
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0)
            ],
            1: [
                (0, 0, 0, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0)
            ],
            2: [
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0),
                (7, 7, 7, 7, 0),
                (0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0)
            ],
            3: [
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 7, 0, 0),
                (0, 0, 0, 0, 0)
            ]
        },
    }
    return blocks[piece][state]