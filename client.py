from ext.utils import Core
from constants import config
from log import log

from datetime import datetime
from aiohttp import ClientSession

import discord
import asyncpg
from discord import Client, Intents
from discord.app_commands import CommandTree


class Dispy(Client):
    https_session: ClientSession

    def __init__(self) -> None:
        self.owner_id = int(config.bot.owner_id)
        super().__init__(
            intents=Intents(),
            application_id=config.bot.app_id,
            owner_id=self.owner_id
        )
        self.launch_time = datetime.now()
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        self.https_session = ClientSession()

        self.tree.add_command(Core(), guild=discord.Object(id=config.debug.guild))
        await self.tree.sync(guild=discord.Object(id=config.debug.guild))
        await self.tree.sync()

    async def close(self) -> None:
        await self.https_session.close()
        await super().close()

    @staticmethod
    async def on_ready() -> None:
        log.info("Ready")
