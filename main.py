import asyncio
from core.core import Core
from instance.four import Four

#TODO:
# === Handling ===

# - Implement GRAVITY
# - Soft Drop Facor: The factor the soft dropping scales the current gravity by

# - Implement Prefer Soft Drop Over Movement: At very high speeds, the soft drop action will be prioritized over movement

# - LOCK DELAY MECHANICS & LOCKING (yes game logic but need this for PrevAccHD)

# - Implement Prevent Accidental Hard Drops: When a piece locks on its own, the harddrop action is disabled for a few frames

#  === game logic ===
# - PERFECT CLEAR DETECTION
# - COMBO DETECTION
# - SCORING
# - LEVELS
# - GAME OVER CONDITIONS

async def main():
    game_instance = Core()
    four = Four(game_instance)
    await game_instance.run(four)

if __name__ == "__main__":
    asyncio.run(main())
