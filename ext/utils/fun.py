from utils.activity import create_together_url, together_choices, together_apps
from utils.cooldowns import Btypes, koeldown

from datetime import datetime, timedelta

from discord import Interaction, VoiceChannel, Member
from discord.app_commands import Group, Range, Choice, command, describe, choices


class Fun(Group, name="fun", description="Commands to have some fun with."):
    """Commands to have some fun with."""

    @command(name="activity", description="Shutdown the bot")
    @describe(option="Choose a game to play")
    @koeldown(1, 30, Btypes.guild)
    @koeldown(1, 150, Btypes.user)
    async def _together_act(self, interaction: Interaction, channel: VoiceChannel, option: together_choices) -> None:
        await interaction.response.send_message(
                (await create_together_url(interaction.client, channel.id, together_apps[option])),
                ephemeral=True
            )

    @command(name="mute", description="Mute a certain member.")
    @describe(
        member="The member that is going to be muted.",
        length="Amount of time to mute the member.",
        unit="Unit of time.",
        reason="Why this member is getting muted."
    )
    @choices(unit=[
        Choice(name="Days", value=86400),
        Choice(name="Hours", value=3600),
        Choice(name="Minutes", value=60),
        Choice(name="Seconds", value=1)
    ])
    async def moderation_mute(
            self, interaction: Interaction,
            member: Member,
            length: Range[int, 1, 2419200],
            unit: Choice[int],
            reason: str = "No reason specified"
    ) -> None:
        second_amount = sec if (sec := length*unit.value) < 2419200 else 2419200
        dt = datetime.now().astimezone() + timedelta(seconds=second_amount)

        await member.timeout(dt, reason=reason)
        await interaction.response.send_message(
            f":ok_hand: Muted {member.mention} for `{reason}` until <t:{int(dt.timestamp())}:F>"
        )
