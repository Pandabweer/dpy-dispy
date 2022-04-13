from typing import Optional, Union, Any

from discord import Interaction
from discord.app_commands import CommandTree, ContextMenu, AppCommandError, Command


class CmdTree(CommandTree):
    async def on_error(
        self,
        interaction: Interaction,
        command: Optional[Union[ContextMenu, Command[Any, ..., Any]]],
        error: AppCommandError,
    ) -> None:
        pass
