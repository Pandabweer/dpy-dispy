from __future__ import annotations
import asyncio
import os
import re
from asyncio import AbstractEventLoop
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
from yt_dlp.utils import DownloadError
from discord import (
    Client,
    Guild,
    Interaction,
    VoiceChannel,
    VoiceClient,
    FFmpegPCMAudio,
    PCMVolumeTransformer
)
from discord.errors import ClientException

from constants import config
from ext.music.utils.spotify import convert_spotify, get_spotify_playlist, url_regex
from ext.music.utils.identify import Sites, PlaylistTypes, Origins, identify_playlist, identify_url
from ext.music.utils.song import Song
from ext.music.utils.playlist import Playlist


COOKIE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../cookies/cookies.txt"


class AudioController:
    """Audio controller per guild, this handles all functions regarding audio"""

    voice_client: VoiceClient | None
    playlist: Playlist
    current_song: Song | None
    volume: int
    timer: Timer

    def __init__(self, client: Client, guild: Guild) -> None:
        self.client = client
        self.guild = guild

        self.voice_client = None
        self.playlist = Playlist()
        self.current_song = None
        self.volume = 100

        self.timer = Timer(self.timeout_handler, client.loop)
        self.default_ytdl_options = {
            "format": "bestaudio/best",
            "title": True,
            "cookiefile": COOKIE_PATH,
            "age_limit": 100,
            "quiet": True
        }

    async def connect(self, inter: Interaction, vc_opt: VoiceChannel | None = None, direct_play: bool = False) -> None:
        """This function handles for both 'play' and 'connect' method. Only the command 'connect' allows for moving"""
        try:
            if self.voice_client is None or not self.voice_client.is_connected():
                channel = vc_opt or inter.user.voice.channel
                self.voice_client = await channel.connect(reconnect=True, timeout=None, self_deaf=True)
                if not direct_play:
                    return await inter.response.send_message(f"Connected to {channel.mention}.")

            raise ClientException
        except AttributeError:
            await inter.response.send_message("You are not connected to a voice channel.")
        except ClientException:
            if vc_opt:
                if vc_opt.id == self.voice_client.channel.id and self.voice_client.is_connected():
                    return await inter.response.send_message(f"I'm already connected to {vc_opt.mention}.")

                if self.voice_client.is_connected():
                    await self.voice_client.move_to(vc_opt)
                else:
                    await self.disconnect()
                    self.voice_client = await inter.user.voice.channel.connect(
                        reconnect=True, timeout=None, self_deaf=True)
                await inter.response.send_message(f"Connected to {vc_opt.mention}.")
            else:
                if not direct_play:
                    if self.voice_client.is_connected():
                        await inter.response.send_message("Already connected to a voice channel.")
                    else:
                        await self.disconnect()
                        self.voice_client = await inter.user.voice.channel.connect(
                            reconnect=True, timeout=None, self_deaf=True)
                        await inter.response.send_message(f"Connected to {inter.user.voice.channel.mention}.")

    async def disconnect(self) -> None:
        """
        Basically resets the whole class, keeps the history, also cleans up the voice protocol.
        Gets called if someone uses the leave command or when it reconnects on a force disconnect.
        """

        self.playlist.loop = False
        self.playlist.next(self.current_song)
        self.playlist.playque.clear()
        self.current_song = None
        self.voice_client.stop()
        self.voice_client.cleanup()
        await self.voice_client.disconnect(force=True)

    @staticmethod
    def get_url(content: str) -> str | None:
        if re.search(url_regex, content):
            result = url_regex.search(content)
            url = result.group(0)
            return url
        else:
            return

    def next_song(self) -> None:
        """Invoked after a song is finished. Plays the next song if there is one."""

        next_song = self.playlist.next(self.current_song)
        self.current_song = None

        if next_song is None:
            return

        self.client.loop.create_task(self.play_song(next_song))

    async def prev_song(self) -> None:
        """Loads the last song from the history into the queue and starts it"""

        prev_song = self.playlist.prev(self.current_song)

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            if prev_song == "Dummy":
                self.playlist.next(self.current_song)
                return
            await self.play_song(prev_song)
        else:
            self.voice_client.stop()

    async def play_song(self, song: Song) -> None:
        """Plays a song object"""

        if not self.playlist.loop:  # let timer run thouh if looping
            self.reset_timer()

        if song.title is None:
            if song.host == Sites.Spotify:
                conversion = self.search_youtube(await convert_spotify(song.webpage_url, self.client.http_session))
                song.webpage_url = conversion

            downloader = yt_dlp.YoutubeDL(self.default_ytdl_options)
            song.define(downloader.extract_info(song.webpage_url, download=False))

        self.playlist.add_name(song.title)
        self.current_song = song
        self.playlist.playhistory.append(self.current_song)

        self.voice_client.play(FFmpegPCMAudio(
            song.base_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=lambda e: self.next_song()
        )

        self.guild.voice_client.source = PCMVolumeTransformer(self.guild.voice_client.source)
        self.guild.voice_client.source.volume = float(self.volume) / 100.0

        self.playlist.playque.popleft()

        for song in list(self.playlist.playque)[:config.music.max_song_preload]:
            asyncio.ensure_future(self.preload(song))

    async def preload(self, song: Song) -> None:
        if song.title is not None:
            return

        def down(track: Song):
            if track.host == Sites.Spotify:
                track.webpage_url = self.search_youtube(track.title)

            if track.webpage_url is None:
                return

            downloader = yt_dlp.YoutubeDL(self.default_ytdl_options)
            track.define(downloader.extract_info(track.webpage_url, download=False))

        if song.host == Sites.Spotify:
            song.title = await convert_spotify(song.webpage_url, self.client.http_session)

        executor = ThreadPoolExecutor(max_workers=config.music.max_song_preload)
        await asyncio.wait(
            fs={self.client.loop.run_in_executor(executor, down, song)},
            return_when=asyncio.ALL_COMPLETED
        )

    async def process_song(self, track: str) -> Song:
        """Adds the track to the playlist instance, plays it if it is the first song"""

        host = identify_url(track)
        is_playlist = identify_playlist(track)

        if is_playlist != PlaylistTypes.Unknown:
            await self.process_playlist(is_playlist, track)

            if self.current_song is None:
                await self.play_song(self.playlist.playque[0])

            song = Song(Sites.Unknown, Origins.Playlist)
            return song

        if host == Sites.Unknown:
            if self.get_url(track) is not None:
                return

            track = self.search_youtube(track)

        if host == Sites.Spotify:
            title = await convert_spotify(track, self.client.http_session)
            track = self.search_youtube(title)

        if host == Sites.YouTube:
            track = track.split("&list=")[0]

        try:
            r = None
            downloader = yt_dlp.YoutubeDL(self.default_ytdl_options)
            try:
                r = downloader.extract_info(track, download=False)
            except Exception as e:
                if "ERROR: Sign in to confirm your age" in str(e):
                    return
        except Exception as err:
            print(err)
            downloader = yt_dlp.YoutubeDL({'title': True, "cookiefile": COOKIE_PATH, "quiet": True})
            r = downloader.extract_info(track, download=False)

        if not r:
            return

        song = Song(host, Origins.Default)
        song.define(r, thumbnail=r.get('thumbnails')[len(r.get('thumbnails')) - 1]['url'])

        self.playlist.add(song)
        if self.current_song is None:
            await self.play_song(song)

        return song

    async def process_playlist(self, playlist_type, url) -> None:
        if playlist_type == PlaylistTypes.YouTube_Playlist:
            if "playlist?list=" not in url:
                video = url.split('&')[0]
                return await self.process_song(video)

            with yt_dlp.YoutubeDL(self.default_ytdl_options) as ydl:
                r = ydl.extract_info(url, download=False)

                for entry in r['entries']:
                    link = f"https://www.youtube.com/watch?v={entry['id']}"
                    song = Song(Sites.YouTube, Origins.Playlist, webpage_url=link)

                    self.playlist.add(song)

        if playlist_type == PlaylistTypes.Spotify_Playlist:
            links = await get_spotify_playlist(url, self.client.http_session)
            for link in links:
                song = Song(Sites.Spotify, Origins.Playlist, webpage_url=link)
                self.playlist.add(song)

        if playlist_type == PlaylistTypes.BandCamp_Playlist:
            options = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                "quiet": True
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                r = ydl.extract_info(url, download=False)

                for entry in r['entries']:
                    link = entry.get("url")
                    self.playlist.add(Song(Sites.Bandcamp, Origins.Playlist, webpage_url=link))

        for song in list(self.playlist.playque)[:config.music.max_song_preload]:
            asyncio.ensure_future(self.preload(song))

    def search_youtube(self, title: str) -> str | None:
        """Searches YouTube for the video title and returns the first results video link"""

        # if title is already a link
        if self.get_url(title) is not None:
            return title

        options = self.default_ytdl_options
        options["default_search"] = "auto"
        options["noplaylist"] = True

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                r = ydl.extract_info(title, download=False)
        except DownloadError:
            return

        if r is None:
            return

        return f"https://www.youtube.com/watch?v={r['entries'][0]['id']}"

    def reset_timer(self) -> None:
        self.timer.cancel()
        self.timer = Timer(self.timeout_handler, self.client.loop)

    async def timeout_handler(self) -> None:
        if len(self.voice_client.channel.voice_states) == 1:
            return await self.disconnect()

        vc_timeout = False  # TODO Additional settings
        self.timer = Timer(self.timeout_handler, self.client.loop)

        if not vc_timeout or self.voice_client.is_playing():
            return

        await self.disconnect()


class Timer:
    def __init__(self, callback: Callable, loop: AbstractEventLoop) -> None:
        self._callback = callback
        self._task = loop.create_task(self._job())

    async def _job(self) -> None:
        await asyncio.sleep(config.music.vc_timeout)
        await self._callback()

    def cancel(self) -> None:
        self._task.cancel()
