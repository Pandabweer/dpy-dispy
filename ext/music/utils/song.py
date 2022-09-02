import datetime

from discord import Embed

from ext.music.utils.identify import Sites, Origins


class Song:
    def __init__(self, host: Sites, origin: Origins, base_url: str = None, uploader: str = None,
                 title: str = None, duration: int = None, webpage_url: str = None, thumbnail: str = None):
        self.host = host
        self.origin = origin
        self.base_url = base_url

        self.uploader = uploader
        self.title = title
        self.duration = duration
        self.webpage_url = webpage_url
        self.thumbnail = thumbnail

    def define(self, result: dict, *, thumbnail: str = None) -> None:
        self.base_url = result.get('url')
        self.uploader = result.get('uploader')
        self.title = result.get('title')
        self.duration = result.get('duration')
        self.webpage_url = result.get('webpage_url')
        self.thumbnail = thumbnail or result.get('thumbnails')[0]['url']

    def to_embed(self, playtype: str) -> Embed:
        embed = Embed(title=playtype, description=f"[{self.title}]({self.webpage_url})", color=0xFFF)
        embed.add_field(name="Uploader:", value=self.uploader, inline=False)

        if self.duration is not None:
            embed.add_field(name="Duration:", value=datetime.timedelta(seconds=self.duration), inline=False)

        if self.thumbnail is not None:
            embed.set_thumbnail(url=self.thumbnail)

        return embed
