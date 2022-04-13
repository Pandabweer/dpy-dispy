from log import log

from discord import Interaction
from discord.errors import NotFound
from discord.app_commands import CommandTree, AppCommandError, Command


class CmdTree(CommandTree):
    """A subclass of CommandTree to override on_error"""

    async def on_error(
        self,
        interaction: Interaction,
        command: Command,
        error: AppCommandError,
    ) -> None:
        # Per usual, getting the original error
        error = getattr(error, 'original', error)

        if isinstance(error, NotFound):
            log.debug("Not found error matteee")

        raise error
