from discord import Interaction
from discord.app_commands import CommandTree, AppCommandError, Command
from discord.errors import NotFound, HTTPException, Forbidden
from discord.app_commands.errors import CommandOnCooldown

from log import log


def time_fmt(seconds: float) -> str:
    if seconds < 60:
        left = seconds
        amount = "second(s)"
    elif seconds < 3600:
        left = divmod(seconds, 60)[0]
        amount = "minute(s)"
    else:
        left = divmod(seconds, 3600)[0]
        amount = "hour(s)"

    return f"{int(left)} {amount}"


class CmdTree(CommandTree):
    """A subclass of CommandTree to override on_error"""

    async def on_error(self, interaction: Interaction, command: Command, error: AppCommandError) -> None:
        # Per usual, getting the original error
        error = getattr(error, 'original', error)

        log.debug("Reached error_handler")

        if isinstance(error, (NotFound, HTTPException, Forbidden)):
            log.warn(f"'{interaction.command.name}' command raised {error.status} {error.__class__}")
            raise error
        elif isinstance(error, CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown! Time left: {time_fmt(error.retry_after)}", ephemeral=True)
        else:
            raise error
