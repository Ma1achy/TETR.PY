import asyncio
from pygame_instance import PyGameInstance
from four import Four

#TODO:
# - GAME OVER CONDITIONS
# - GRAVITY
# - LOCK DELAY
# - PERFECT CLEAR DETECTION
# - COMBO DETECTION
# - SCORING
# - LEVELS

async def main():
    pygame_instance = PyGameInstance()
    four = Four(pygame_instance)
    await pygame_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
