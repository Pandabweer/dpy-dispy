import asyncio

from discord import Interaction

from ui.buttons import Confirm


async def inter_timeout(inter: Interaction, view: Confirm, *, after_delete: int = 10) -> bool:
    # Waits for the interaction, if interaction is timed-out view.wait() returns True
    if await view.wait():
        await inter.edit_original_message(content="Command timed out", view=None)
        await asyncio.sleep(after_delete)
        await inter.delete_original_message()
        return False
    return True
