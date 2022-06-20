from datetime import datetime

import asyncio
import discord
import asyncpg
from aiohttp import ClientSession
from discord import Client, Intents

from constants import config
from ext.backend.error_handler import CmdTree
from log import log

from ext.utils import Core, Fnine


class Dispy(Client):
    https_session: ClientSession
    database: asyncpg.connection.Connection
    loop: asyncio.AbstractEventLoop
    mc_proc: asyncio.subprocess.Process

    def __init__(self) -> None:
        self.owner_id = int(config.bot.owner_id)
        super().__init__(
            intents=Intents(),
            application_id=config.bot.app_id,
            owner_id=self.owner_id
        )
        self.launch_time = datetime.now()
        self.tree = CmdTree(self)
        self.loop = asyncio.get_event_loop()

    async def _read_stream_stderr(self, stream) -> None:
        # Waiting for the Discord bot to start
        await self.wait_until_ready()

        while True:
            if line := await stream.readline():
                raw_text = line.decode("UTF-8").replace("\n", "")
                print(raw_text)
            else:
                break

    async def _read_stream_stdout(self, stream) -> None:
        # Waiting for the Discord bot to start
        await self.wait_until_ready()

        while True:
            if line := await stream.readline():
                raw_text = line.decode("UTF-8")
                print(raw_text)
            else:
                break

    async def _mc_subprocess(self) -> None:
        self.mc_proc = await asyncio.create_subprocess_shell(
            "cd Tekkit_Server_v1.2.9g-2 && java -Xmx16G -Xms15G -jar Tekkit.jar nogui",
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
            )

        await asyncio.wait([
            asyncio.create_task(self._read_stream_stderr(self.mc_proc.stderr)),
            asyncio.create_task(self._read_stream_stdout(self.mc_proc.stderr))
        ])

    async def setup_hook(self) -> None:
        self.database = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            database="dispy",
            password="Vadersgroet5"
            )
        self.https_session = ClientSession()

        self.tree.add_command(Core(), guild=discord.Object(id=config.debug.guild))
        self.tree.add_command(Fnine(), guild=discord.Object(id=config.debug.guild))
        await self.tree.sync(guild=discord.Object(id=config.debug.guild))
        if config.debug.global_cmds:
            await self.tree.sync()

        asyncio.create_task(self._mc_subprocess())

    async def close(self) -> None:
        await self.database.close()
        await self.https_session.close()
        self.mc_proc.terminate()
        await super().close()

    @staticmethod
    async def on_ready() -> None:
        log.info("Ready")
