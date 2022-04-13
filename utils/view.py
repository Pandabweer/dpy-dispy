import asyncio
from typing import Type

from discord import Interaction
from discord.ui import View


async def inter_timeout(inter: Interaction, view: Type[View]) -> bool:
    # Waits for the interaction, if interaction is timed-out view.wait() returns True
    if await view.wait():
        await inter.edit_original_message(content="Command timed out", view=None)
        await asyncio.sleep(10)
        await inter.delete_original_message()
        return False
    return True
