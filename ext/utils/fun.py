from utils.activity import create_together_url, together_choices, together_apps
from decorators import is_bot_owner

from discord import Interaction, VoiceChannel
from discord.app_commands import Group, command, describe, check


class Fun(Group, name="fun", description="Commands to have some fun with."):
    """Commands to have some fun with."""

    @command(name="activity", description="Shutdown the bot")
    @describe(option="Choose a game to play")
    @check(is_bot_owner)
    async def _stop_bot(self, interaction: Interaction, channel: VoiceChannel, option: together_choices) -> None:
        await interaction.response.send_message(
                (await create_together_url(interaction.client, channel.id, together_apps[option])),
                ephemeral=True
            )
