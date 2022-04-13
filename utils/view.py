import asyncio
from typing import Any

from discord import Interaction
from discord.ui import View


async def inter_timeout(inter: Interaction, view: Any):
    return