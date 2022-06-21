import asyncio

from typing import Literal

from discord import Interaction
from discord.app_commands import Group, command, describe, check

from decorators import is_bot_owner
from log import log


class ServerHandler(Group, name="server", description="Handles servers and communication between the bot."):
    """Handles servers and communication between the bot."""

    def __init__(self) -> None:
        super().__init__()
        self.tekkit_task = None

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
            self.loop.create_task(self._read_stream_stderr(self.mc_proc.stderr)),
            self.loop.create_task(self._read_stream_stdout(self.mc_proc.stderr))
        ])

    async def tekkit(self):
        while True:
            await asyncio.sleep(3)
            log.warn("tekkit running...")

    @command(name="start", description="Start a server")
    @check(is_bot_owner)
    async def _start_server(self, interaction: Interaction, server: Literal["Tekkit", "Vanilla"]) -> None:
        if server == "Tekkit":
            if self.tekkit_task is None:
                self.tekkit_task = interaction.client.loop.create_task(self.tekkit())
                await interaction.response.send_message("Starting tekkit server...")
            else:
                if self.tekkit_task.cancelled():
                    self.tekkit_task = interaction.client.loop.create_task(self.tekkit())
                    await interaction.response.send_message("Starting tekkit server...")
                else:
                    await interaction.response.send_message("Tekkit server is already online.")
        elif server == "Vanilla":
            pass

    @command(name="stop", description="Stop a server")
    @check(is_bot_owner)
    async def _stop_server(self, interaction: Interaction, server: Literal["Tekkit", "Vanilla"]) -> None:
        if server == "Tekkit":
            if self.tekkit_task is None:
                await interaction.response.send_message("Tekkit server is already offline.")
            else:
                if self.tekkit_task.cancelled():
                    await interaction.response.send_message("Tekkit server is already offline.")
                else:
                    self.tekkit_task.cancel()
                    await interaction.response.send_message("Shutting down the tekkit server.")
        elif server == "Vanilla":
            pass
