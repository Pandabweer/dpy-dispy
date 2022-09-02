from discord import Interaction, VoiceChannel
from discord.app_commands import Group, command, describe

from ext.music.utils.identify import Origins
from ext.music.utils.audiocontroller import AudioController

from ext.music.view.main_ui import PlayerView

# Add all neccecary commands
# Fix regex double search

# Cached music
# Add own async extractor
# Max cached songs + amount listed keep mostly listened songs
# Fix previous song adding duplicated on multiple command invokes
# Player interactable


class Music(Group, name="music", description="Music player, to provide music inside Discord."):
    """Music player, to provide music inside Discord."""

    def __init__(self) -> None:
        super().__init__()
        self.guild_audio_controllers: dict[AudioController] = {}

    def get_audio_controller(self, inter: Interaction) -> AudioController:
        if not self.guild_audio_controllers.get(inter.guild.id):
            self.guild_audio_controllers[inter.guild.id] = AudioController(inter.client, inter.guild)

        return self.guild_audio_controllers[inter.guild.id]

    @command(name="connect", description="Connect bot or move to a voice channel.")
    @describe(channel="Specific channel to connect to")
    async def _vc_connect(self, interaction: Interaction, channel: VoiceChannel = None) -> None:
        await self.get_audio_controller(interaction).connect(interaction, channel)

    @command(name="leave", description="Disconnect bot from the current voice channel.")
    async def _vc_disconnect(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)
        if not audiocontroller.guild.voice_client:
            return await interaction.response.send_message("I'm not in a voice channel.")

        await audiocontroller.disconnect()
        await interaction.response.send_message("Disconnected")

    @command(name="play", description="Play a song trough the bot.")
    async def _song_add(self, interaction: Interaction, track: str) -> None:
        audiocontroller = self.get_audio_controller(interaction)
        await audiocontroller.connect(interaction, direct_play=True)

        if interaction.response.is_done():
            return

        audiocontroller.reset_timer()

        if audiocontroller.playlist.loop:
            return await interaction.response.send_message("Loop is enabled! Use the loop command to disable.")

        await interaction.response.send_message(f"Searching for: {track}")

        song = await audiocontroller.process_song(track)

        if song is None:
            return await interaction.edit_original_message(
                content="Unsupported site or age restricted content or video unavailable.")

        if song.origin == Origins.Default:
            if audiocontroller.current_song is not None and len(audiocontroller.playlist.playque) == 0:
                await interaction.edit_original_message(embed=song.to_embed("Now Playing"))
            else:
                await interaction.edit_original_message(embed=song.to_embed("Added to queue"))

        elif song.origin == Origins.Playlist:
            await interaction.edit_original_message(content="Queued playlist :page_with_curl:")

    @command(name="pause", description="Pause the current song")
    async def _song_pause(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)

        if audiocontroller.voice_client is None or not audiocontroller.voice_client.is_connected():
            return await interaction.response.send_message("I'm not connected to a channel.")

        if audiocontroller.voice_client.is_paused():
            return await interaction.response.send_message("Song is already paused.")

        audiocontroller.voice_client.pause()
        await interaction.response.send_message("Paused the current song.")

    @command(name="resume", description="Resume the current song")
    async def _song_resume(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)

        if audiocontroller.voice_client is None or not audiocontroller.voice_client.is_connected():
            return await interaction.response.send_message("I'm not connected to a channel.")

        if not audiocontroller.voice_client.is_paused():
            return await interaction.response.send_message("Song is not paused.")

        audiocontroller.voice_client.resume()
        await interaction.response.send_message("Resumed the current song.")

    @command(name="skip", description="Skip the current song")
    async def _song_skip(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)

        if audiocontroller.voice_client is None or not audiocontroller.voice_client.is_connected():
            return await interaction.response.send_message("I'm not connected to a channel.")

        if audiocontroller.voice_client is None or (
                not audiocontroller.voice_client.is_paused() and not audiocontroller.voice_client.is_playing()):
            return await interaction.response.send_message("Queue is empty.")

        audiocontroller.playlist.loop = False
        audiocontroller.reset_timer()

        audiocontroller.voice_client.stop()
        await interaction.response.send_message("Skipped current song.")

    @command(name="previous", description="Plays the previous song")
    async def _song_previous(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)

        if audiocontroller.voice_client is None or not audiocontroller.voice_client.is_connected():
            return await interaction.response.send_message("I'm not connected to a channel.")

        if len(audiocontroller.playlist.playhistory) == 1 and audiocontroller.voice_client.is_playing():
            return await interaction.response.send_message("There is no previous song.")

        audiocontroller.playlist.loop = False
        audiocontroller.reset_timer()

        await audiocontroller.prev_song()
        await interaction.response.send_message("Playing previous song.")

    @command(name="loop", description="Loops the current song")
    async def _song_loop(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)

        if audiocontroller.voice_client is None or not audiocontroller.voice_client.is_connected():
            return await interaction.response.send_message("I'm not connected to a channel.")

        if len(audiocontroller.playlist.playque) < 1 and not audiocontroller.voice_client.is_playing():
            return await interaction.response.send_message("Nothing is playing.")

        switch = audiocontroller.playlist.loop = not audiocontroller.playlist.loop

        await interaction.response.send_message(
            f"Loop {'enabled' if switch else 'disabled'} for {audiocontroller.current_song.title}")

    @command(name="player", description="Music player with UI")
    async def _music_player(self, interaction: Interaction) -> None:
        audiocontroller = self.get_audio_controller(interaction)
        await interaction.response.send_message("Test", view=PlayerView(audiocontroller))
