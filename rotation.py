from vec2 import Vec2 
# TODO: switch to predefined kick tables for kicks between rotation states rather than using offsets
# and calculating the offsets on the fly, as 
# 
# 1/ kick tables for different rotation systems are documented far better
# 2/ kick tables are easier to understand and maintain

# I 180 kicks are definitely wrong, when rotating between 0 and 2 the I piece should wobble up and down (instead wobbles side to side)
# when rotating between 1 and 3 the I piece should wobble side to side (instead wobbles up and down)

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

O_OFFSETS = ([ 
    [(Vec2(0, 0))],
    [(Vec2(0, -1))],
    [(Vec2(-1, -1))],
    [(Vec2(-1, 0))],
])

TSZLKJ_180_OFFSETS = ([
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, 1),   Vec2(2, 1),   Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, 1),  Vec2(-2, 1),  Vec2(0, -1), Vec2(3, 0),  Vec2(-3, 0)]),
    ([Vec2(0, -1), Vec2(0, 1),  Vec2(0, 2),  Vec2(-1, 1),  Vec2(-1, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, -1), Vec2(-1, -2), Vec2(1, 0),  Vec2(0, 3),  Vec2(0, -3)]),
    ([Vec2(-1, -1), Vec2(-1, 0), Vec2(-2, 0), Vec2(-1, -1), Vec2(-2, -1), Vec2(1, 0),  Vec2(2, 0),  Vec2(1, -1),  Vec2(2, -1),  Vec2(0, 1),  Vec2(-3, 0), Vec2(3, 0)]),
    ([Vec2(-1, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(1, 1),   Vec2(1, 2),   Vec2(0, -1), Vec2(0, -2), Vec2(1, -1),  Vec2(1, -2),  Vec2(-1, 0), Vec2(0, 3),  Vec2(0, -3)])
])

I_180_OFFSETS = (
    ([Vec2(0, 0), Vec2(-1, 0), Vec2(-2, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(0, 1),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(-1, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(1, 0),  Vec2(2, 0),  Vec2(-1, 0), Vec2(-2, 0), Vec2(0, -1), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)]),
    ([Vec2(0, 0), Vec2(0, 1),  Vec2(0, 2),  Vec2(0, -1), Vec2(0, -2), Vec2(1, 0),  Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0)])
)