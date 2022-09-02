import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime

import asyncpg
import discord
from aiohttp import ClientSession
from asyncpg.connection import Connection
from discord import Client, Intents, AppInfo, AllowedMentions

from constants import config
from ext.backend.api import DispyApi
from ext.backend.error_handler import CmdTree
from log import log
from utils.extensions import EXTENSIONS


class Dispy(Client):
    app_info: AppInfo
    database: Connection

    def __init__(self) -> None:
        self.loop: AbstractEventLoop = asyncio.get_event_loop()
        self.owner_id: int = int(config.bot.owner_id)
        super().__init__(
            intents=Intents(guilds=True, voice_states=True),
            application_id=config.bot.app_id,
            allowed_mentions=AllowedMentions(everyone=False),
            owner_id=self.owner_id
            )
        self.launch_time: datetime = datetime.now()
        self.http_session: ClientSession = ClientSession()
        self.tree: CmdTree = CmdTree(self)

    async def __start_database(self) -> None:
        self.database = await asyncpg.connect(
            host=config.db.host, port=config.db.port,
            user=config.db.user, database=config.db.database,
            password=config.db.password
            )

    async def __slash_load(self) -> None:
        for extension in EXTENSIONS:
            self.tree.add_command(extension(), guild=discord.Object(id=config.debug.guild))

        await self.tree.sync(guild=discord.Object(id=config.debug.guild))
        if config.debug.global_cmds:
            await self.tree.sync()

    async def setup_hook(self) -> None:
        self.app_info = await self.application_info()
        log.info(f"Starting {self.app_info.name} using discord.py {discord.__version__} - {discord.__copyright__}")

        await self.__start_database()
        await self.__slash_load()
        # await asyncio.create_subprocess_shell("py dashboard/app.py")
        self.loop.create_task(DispyApi().start(self))

    @property
    def latency(self) -> int:
        return int(super().latency * 1000)

    async def on_ready(self) -> None:
        log.info(f"Ready, {self.latency}ms")

    async def close(self) -> None:
        log.info("Shutdown command received.")
        await self.database.close()
        await self.http_session.close()
        await super().close()
