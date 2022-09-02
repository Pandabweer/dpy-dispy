from discord import Interaction, VoiceChannel
from discord import ButtonStyle, SelectOption, TextStyle, ui
from discord.ui import View, Button, Select

from ext.music.utils.audiocontroller import AudioController


class PlayerVoiceChannels(Select):
    def __init__(self, audiocontroller: AudioController) -> None:
        self.audiocontroller = audiocontroller

        options = [
            SelectOption(label=vc.name, value=vc.id, emoji="🔊") for vc in audiocontroller.guild.voice_channels
        ]

        super().__init__(placeholder='Choose a voice channel...', options=options)

    async def get_vchannel(self, channel_id: int) -> VoiceChannel:
        return (
                self.audiocontroller.guild.get_channel(channel_id) or
                await self.audiocontroller.guild.fetch_channel(channel_id)
            )

    async def callback(self, interaction: Interaction) -> None:
        channel = await self.get_vchannel(int(self.values[0]))
        self.audiocontroller.voice_client = await channel.connect(reconnect=True, timeout=None, self_deaf=True)
        await interaction.response.edit_message(content="kaas")


class PlayerView(View):
    def __init__(self, audiocontroller: AudioController, timeout: float = 300.0) -> None:
        super().__init__(timeout=timeout)
        self.add_item(PlayerVoiceChannels(audiocontroller))

        self.audiocontroller = audiocontroller

    @ui.button(emoji="⏮")
    async def music_previous(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.edit_message(content="reverse", view=None)
        self.stop()

    @ui.button(emoji="⏯")
    async def music_pause_or_play(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.edit_message(content="playorpause", view=None)
        self.stop()

    @ui.button(emoji="⏭")
    async def music_next(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.edit_message(content="playorpause", view=None)
        self.stop()


