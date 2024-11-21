import asyncio
from core.core import Core
from instance.four import Four

#TODO:

# - check if when prefSD is true if the order of preform actions and gravity needs to be swapped in game loop. 90% sure i dont have to worry about this but lmao icba to check

#  === game logic ===
# - PERFECT CLEAR DETECTION 
# - COMBO DETECTION
# - SCORING
# - LEVELS

# ARE - entry delay 
# line clear delay
# -> when blocks r attempted to be pushed up into line -1  (from garbage or whatever) -> game over ('top out' condition)
# basically to prevent out of index error lmao, but also can just disable this and just delete rows when they are pushed up from line 0

# TODO: implement das cut delay

async def main():
    game_instance = Core()
    four = Four(game_instance.Config, game_instance.FlagStruct, game_instance.GameInstanceStruct, game_instance.TimingStruct, game_instance.HandlingStruct, game_instance.HandlingConfig, matrix_width = 10, matrix_height = 20, rotation_system = 'SRS', randomiser = '7BAG', queue_previews = 5,  seed = 0, hold = True, allowed_spins = 'ALL-MINI', lock_out_ok = True, top_out_ok = False, reset_on_top_out = False)
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())