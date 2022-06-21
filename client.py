from constants import config
from log import log
from utils.extensions import EXTENSIONS
from ext.backend.error_handler import CmdTree

import asyncio
from datetime import datetime

import discord
import asyncpg
from aiohttp import ClientSession
from discord import Client, Intents, AppInfo, AllowedMentions


class Dispy(Client):
    app_info: AppInfo
    database: asyncpg.connection.Connection
    http_session: ClientSession

    def __init__(self) -> None:
        self.owner_id: int = int(config.bot.owner_id)
        super().__init__(
            intents=Intents(guilds=True),
            application_id=config.bot.app_id,
            allowed_mentions=AllowedMentions(everyone=False),
            owner_id=self.owner_id
        )
        self.launch_time: datetime = datetime.now()
        self.tree: CmdTree = CmdTree(self)
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    @property
    def latency(self) -> int:
        return int(super().latency * 1000)

    async def on_ready(self) -> None:
        log.info(f"Ready, {self.latency}ms")

    async def setup_hook(self) -> None:
        self.app_info = await self.application_info()
        log.info(f"Starting {self.app_info.name} using discord.py {discord.__version__} - {discord.__copyright__}")

        self.database = await asyncpg.connect(
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            database=config.db.database,
            password=config.db.password
            )
        self.http_session = ClientSession()

        for extension in EXTENSIONS:
            self.tree.add_command(extension(), guild=discord.Object(id=config.debug.guild))

        await self.tree.sync(guild=discord.Object(id=config.debug.guild))
        if config.debug.global_cmds:
            await self.tree.sync()

    async def close(self) -> None:
        log.info("Shutdown command received.")
        await self.database.close()
        await self.http_session.close()
        await super().close()
