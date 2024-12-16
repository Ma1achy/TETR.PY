import asyncio
from core.core import Core
from instance.engine.four import Four

async def main():
    game_instance = Core()
    four = Four(game_instance.Config, game_instance.FlagStruct, game_instance.GameInstanceStruct, game_instance.TimingStruct, game_instance.HandlingStruct, game_instance.HandlingConfig, matrix_width = 10, matrix_height = 20, rotation_system = 'SRS', randomiser = '7BAG', queue_previews = 5,  seed = 0, hold = True, allowed_spins = 'ALL-MINI', lock_out_ok = True, top_out_ok = False, reset_on_top_out = False)
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())