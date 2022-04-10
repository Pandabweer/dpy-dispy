from ui.buttons import Confirm
from decorators import is_bot_owner
from log import log

import asyncio
import os
import sys

from discord import Interaction
from discord.app_commands import Group, command, describe, check


class Core(Group, name="core"):
    """Core functionality of the bot"""

    @command(name="stop", description="Shutdown the bot")
    @describe(forced="Forced shutdown of the bot")
    @check(is_bot_owner)
    async def _stop_bot(self, interaction: Interaction, forced: bool = False) -> None:
        view = Confirm(
            conf_msg="Shutting down the bot.",
            canc_msg="Cancled bot shutdown."
        )

        await interaction.response.send_message("Are you sure you want to shut the bot?", view=view)

        if await view.wait():
            await interaction.edit_original_message(content="Command timed out", view=None)
            await asyncio.sleep(10)
            await interaction.delete_original_message()
        else:
            if view.value:
                log.info("Shutdown command received")
                if forced:
                    exit(0)
                await interaction.client.close()

    @command(name="restart", description="Restarts the bot")
    @check(is_bot_owner)
    async def _restart_bot(self, interaction: Interaction) -> None:
        view = Confirm(
            conf_msg="Restarting down the bot.",
            canc_msg="Cancled bot restart."
        )

        await interaction.response.send_message("Are you sure you want to restart the bot?", view=view)

        if await view.wait():
            await interaction.edit_original_message(content="Command timed out", view=None)
            await asyncio.sleep(10)
            await interaction.delete_original_message()
        else:
            if view.value:
                log.info("Restart command received")
                os.execv(sys.executable, ['python'] + sys.argv)
