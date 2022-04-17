from discord import Interaction
from discord.app_commands import CommandTree, AppCommandError, Command
from discord.errors import NotFound, HTTPException, Forbidden

from log import log


class CmdTree(CommandTree):
    """A subclass of CommandTree to override on_error"""

    async def on_error(self, interaction: Interaction, command: Command, error: AppCommandError) -> None:
        # Per usual, getting the original error
        error = getattr(error, 'original', error)

        log.debug("Reached error_handler")

        if isinstance(error, (NotFound, HTTPException, Forbidden)):
            log.warn(f"'{interaction.command.name}' command raised {error.status} {error.__class__}")
            raise error
        else:
            raise error
